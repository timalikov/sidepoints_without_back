from typing import Any, Callable
import discord
from services.messages.customer_support_messenger import send_message_to_customer_support
from services.messages.interaction import send_interaction_message

class RefundReplaceView(discord.ui.View):
    def __init__(
        self,
        *, 
        customer: discord.User,
        kicker: discord.User
    ) -> None:
        super().__init__(timeout=None)
        self.customer = customer
        self.kicker = kicker
        self.already_pressed = False

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)
                self.already_pressed = True
                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message="Button already pressed"
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

        # Refund logic

        await send_interaction_message(
            interaction=interaction,
            message=f"Okay your payment will be refunded soon."
        )
        try:
            await self.kicker.send(f"User <@{self.customer.id}> refunded the payment!")
        except discord.HTTPException:
            print(f"Failed to send message to kicker {self.kicker.id}")


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
            message=f"User <@{self.customer.id}> wants to replace the kicker: <@{self.kicker.id}>"
        )

        await send_interaction_message(
            interaction=interaction,
            message="Customer support will contact you soon and replace your kicker."
        )