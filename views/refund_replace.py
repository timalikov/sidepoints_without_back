from typing import Any, Callable
from bot_instance import get_bot
import discord
from services.messages.customer_support_messenger import send_message_to_customer_support
from services.messages.interaction import send_interaction_message
from services.refund_handler import RefundHandler
from services.timeout_refund_handler import TimeoutRefundHandler

bot = get_bot()

class RefundReplaceView(discord.ui.View):
    def __init__(
        self,
        *, 
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        sqs_client: Any,
        timeout: int = 5,
        channel: Any = None,
        invite_url: str = None,
        stop_task: Callable = None, 

    ) -> None:
        super().__init__(timeout=None)
        self.customer = customer
        self.kicker = kicker
        self.purchase_id = purchase_id
        self.sqs_client = sqs_client
        self.timeout = timeout
        self.channel = channel
        self.invite_url = invite_url
        self.stop_task = stop_task if stop_task is not None else lambda: None
        self.already_pressed = False
        self.refund_handler = RefundHandler(sqs_client, purchase_id, customer, kicker)
        # self.services_db = Services_Database()
        # self.service = self.services_db.get_services_by_username(kicker.name)

        self.timeout_refund_handler = TimeoutRefundHandler(
            timeout_seconds= 60 * self.timeout,
            on_timeout_callback=self.auto_refund  
        )

    async def auto_refund(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        message=f"Sorry, we haven't received your decision in 5 minutes. The funds will be automatically refunded to your wallet."
        self.customer.send(content=message)

        await self.refund_handler.process_refund(
            interaction=None,
            success_message="",
            kicker_message=f"User <@{self.customer.id}> refunded the payment!",
            customer_message=None,
            channel=self.channel
        )


    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)

                self.already_pressed = True
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                
                await interaction.message.edit(view=self)
                
                if self.stop_task:
                    self.stop_task()

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
            interaction=None,
            success_message="Your funds will be refunded to your wallet soon! Until then, you can search for a new kicker.",
            kicker_message=f"User <@{self.customer.id}> refunded the payment!",
            customer_message=f"Your funds will be refunded to your wallet soon! Until then, you can search for a new kicker.",
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
        

        await send_message_to_customer_support(
            bot=bot,
            message=(
                "**Replacement has been purchased**\n"
                f"User: <@{self.customer.id}>\n"
                f"Kicker: <@{self.kicker.id}>\n"
                # f"Service: {self.service['service_price']}\n"
                f"Voice room: {self.invite_url if self.invite_url else 'Not available'}"
            )
        )

        await send_interaction_message(
            interaction=interaction,
            message=f"The replacement has been requested. Please wait in the Voice room {self.invite_url}."
        )

        await self.kicker.send(
            "The replacement has been requested:\n"
            f"User: <@{self.customer.id}>\n"
        )

