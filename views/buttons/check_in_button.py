from typing import Literal
import asyncio
import discord
import requests

from config import CHECK_IN_URL, CHECK_IN_AVAILABLE
from translate import translations
from bot_instance import get_bot

from models.payment import get_jwt_token
from services.logger.client import CustomLogger
from services.messages.interaction import send_interaction_message
from services.common_http import handle_status_code
from views.buttons.base_button import BaseButton

logger = CustomLogger
bot = get_bot()


class CheckInButton(BaseButton):
    def __init__(
        self,
        *,
        user: discord.User,
        total_points: int,
        lang: Literal["en", "ru"] = "en",
        row: int | None = None
    ) -> None:
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Daily check in",
            row=row
        )
        self.total_points = total_points
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(
            description=translations["task_completed_message"][self.lang].format(
                total_points=self.total_points + 10
            ),
            colour=discord.Colour.green()
        )
        await send_interaction_message(interaction=interaction, embed=embed)

