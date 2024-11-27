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
        self.token = get_jwt_token(user)
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.total_points = total_points
        self.lang = lang
        self.disabled = True
        try:
            response = requests.get(CHECK_IN_AVAILABLE, timeout=5, headers=self.headers)
        except requests.Timeout:
            logger.http_error_sync("Check in available [timeout]", response)
        if response.status_code != 200:
            logger.http_error_sync("Check in available", response)
        else:
            if response.json():
                self.disabled = False

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        response = requests.post(
            url=CHECK_IN_URL,
            json={
                "discordId": str(interaction.user.id)
            },
            headers=self.headers
        )
        is_success = await handle_status_code(response)
        if is_success:
            embed = discord.Embed(
                description=translations["task_completed_message"][self.lang].format(
                    total_points=self.total_points + 10
                ),
                colour=discord.Colour.green()
            )
        else:
            embed = discord.Embed(
                description=translations["already_checked_in_message"][self.lang],
                colour=discord.Colour.red()
            )
        await send_interaction_message(interaction=interaction, embed=embed)

