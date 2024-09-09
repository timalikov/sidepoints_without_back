from typing import Any, Callable
from bot_instance import get_bot
import discord
from services.messages.interaction import send_interaction_message
from views.refund_replace import RefundReplaceView

bot = get_bot()

class SessionCheckView(discord.ui.View):
    def __init__(
        self, 
        *, 
        customer: discord.User,
        kicker: discord.User,
        
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
        label="Yes",
        style=discord.ButtonStyle.green,
        custom_id="yes_button"
    )
    @check_already_pressed
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await send_interaction_message(
            interaction=interaction,
            message="Okay, enjoy your session!"
        )
        await interaction.message.delete()

    @discord.ui.button(
        label="No",
        style=discord.ButtonStyle.red,
        custom_id="no_button"
    )
    @check_already_pressed
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await send_interaction_message(
            interaction=interaction,
            message="Okay, please select refund or replace kicker."
        )

        view = RefundReplaceView(
            customer=self.customer,
            kicker=self.kicker
        )
        embed_message = discord.Embed(
            colour=discord.Colour.blue(),
            description="Would you like a refund or replace the kicker?"
        )
        await interaction.message.edit(content=None, embed=embed_message, view=view)