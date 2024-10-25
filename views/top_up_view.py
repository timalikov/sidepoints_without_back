from typing import Literal

import discord
from discord.ui import View
import requests

from config import TOP_UP_URL
from translate import translations

from database.dto.psql_discord_profiles import DiscordProfilesDTO
from services.messages.interaction import send_interaction_message
from services.logger.client import CustomLogger

logger = CustomLogger


class TopUpView(View):
    """
    View special for core command top-up.
    """

    def __init__(self, amount: float, lang: Literal["en", "ru"] = "en"):
        super().__init__(timeout=180)
        self.amount = amount
        self.lang = lang

    async def _get_top_up_url(self, url: str, user_discord_id: int) -> str:
        dto = DiscordProfilesDTO()
        wallet = await dto.get_wallet_by_discord_id(user_discord_id)
        request_data = {
            "price": str(self.amount),
            "discord_id": str(user_discord_id),
            "wallet_to_pay": wallet,
            "challenge_id": "5234e156-f328-4902-a832-815bc90504d5",
            "success_url": "https://apptest.sidekick.fans/topup/?topup_status=success",
            "fail_url": "https://apptest.sidekick.fans/topup/?topup_status=fail"
        }
        response = requests.post(url=url, json=request_data)
        if response.status_code != 200:
            logger.http_error("TOP UP", response=response)
            return None
        return response.text

    @discord.ui.button(label="Opbnb", style=discord.ButtonStyle.success)
    async def opbnb(self, interaction: discord.Interaction, button: discord.ui.Button):
        dto = DiscordProfilesDTO()
        wallet = await dto.get_wallet_by_discord_id(interaction.user.id)
        await send_interaction_message(
            interaction=interaction,
            message=translations["opbnb_balance_message"][self.lang].format(wallet=wallet)
        )

    @discord.ui.button(label="Binance", style=discord.ButtonStyle.success)
    async def binance(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        top_up_response_url = await self._get_top_up_url(
            url=TOP_UP_URL + "binance",
            user_discord_id=interaction.user.id
        )
        await send_interaction_message(
            interaction=interaction,
            message=top_up_response_url
        )

    @discord.ui.button(label="Sellix", style=discord.ButtonStyle.success)
    async def sellix(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        top_up_response_url = await self._get_top_up_url(
            url=TOP_UP_URL + "sellix",
            user_discord_id=interaction.user.id
        )
        await send_interaction_message(
            interaction=interaction,
            message=top_up_response_url
        )

    @discord.ui.button(label="Freecasa", style=discord.ButtonStyle.success)
    async def freecasa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        top_up_response_url = await self._get_top_up_url(
            url=TOP_UP_URL + "free-kassa",
            user_discord_id=interaction.user.id
        )
        error_message = translations["server_error_payment"][self.lang]
        await send_interaction_message(
            interaction=interaction,
            message=top_up_response_url if top_up_response_url else error_message
        )
