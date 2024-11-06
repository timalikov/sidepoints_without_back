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

logger = CustomLogger
bot = get_bot()


class CheckInButton(discord.ui.Button):

    def __init__(
        self,
        *,
        user: discord.User,
        total_points: int,
        lang: Literal["en", "ru"] = "en",
        row: int | None = None
    ) -> None:
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Daily check in",
            row=row
        )
        self.token = asyncio.run_coroutine_threadsafe(
            get_jwt_token(user), loop=bot.loop
        )
        self.total_points = total_points
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            url=CHECK_IN_URL,
            json={
                "discordId": str(interaction.user.id)
            },
            headers=headers
        )
        is_success = handle_status_code(response)
        if is_success:
            embed = discord.Embed(
                description=translations["task_completed_message"]["lang"].format(
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

