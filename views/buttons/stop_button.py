from typing import Literal
import discord

from translate import translations

from services.logger.client import CustomLogger

logger = CustomLogger


class StopButton(discord.ui.View):
    def __init__(self, stop_callback, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.stop_callback = stop_callback
        self.lang = lang

    @discord.ui.button(label="Stop notifications", style=discord.ButtonStyle.danger)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.stop_callback():
            message = translations["stopped_notifications"][self.lang]
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=False)
            else:
                await interaction.response.send_message(message, ephemeral=False)
        else:
            await logger.error_discord("Failed to stop all notifications")
