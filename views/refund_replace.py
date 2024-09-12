from typing import Any, Callable
from bot_instance import get_bot
import discord
from services.messages.customer_support_messenger import send_message_to_customer_support
from services.messages.interaction import send_interaction_message
from services.refund_handler import RefundHandler

bot = get_bot()

class RefundReplaceView(discord.ui.View):
    def __init__(
        self,
        *, 
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        sqs_client: Any,
        channel: Any
    ) -> None:
        super().__init__(timeout=None)
        self.customer = customer
        self.kicker = kicker
        self.purchase_id = purchase_id
        self.sqs_client = sqs_client
        self.channel = channel
        self.already_pressed = False
        self.refund_handler = RefundHandler(sqs_client, purchase_id, customer, kicker)

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)

                self.already_pressed = True
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                
                await interaction.message.edit(view=self)

                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message="Button has already been pressed."
                )
            
        return decorator

    @discord.ui.button(
        label="Refund",
        style=discord.ButtonStyle.red,
        custom_id="refund_button"
    )
    @check_already_pressed
    async def refund_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)

        await self.refund_handler.process_refund(
            interaction=interaction,
            success_message="Okay your payment will be refunded soon.",
            kicker_message=f"User <@{self.customer.id}> refunded the payment!",
            customer_message=None,
            channel=self.channel
        )



    @discord.ui.button(
        label="Replace Kicker",
        style=discord.ButtonStyle.green,
        custom_id="replace_button"
    )
    @check_already_pressed
    async def replace_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)

        await self.refund_handler.process_refund(
            interaction=interaction,
            success_message="Okay your payment will be refunded soon.",
            kicker_message=f"User <@{self.customer.id}> refunded the payment!",
            customer_message=None,
            channel=self.channel
        )

        await send_message_to_customer_support(
            bot=bot,
            message=f"User <@{self.customer.id}> wants to replace the kicker: <@{self.kicker.id}>"
        )

        await send_interaction_message(
            interaction=interaction,
            message="Customer support will contact you soon and replace your kicker."
        )