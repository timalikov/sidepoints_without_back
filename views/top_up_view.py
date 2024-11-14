from typing import Literal, List

import discord
from discord.ui import View
import requests

from config import (
    TOP_UP_URL,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME,
    MAIN_GUILD_ID,
)
from translate import translations
from bot_instance import get_bot

from models.payment import get_server_wallet_by_discord_id, get_usdt_balance_by_discord_user
from models.public_channel import get_or_create_channel_by_category_and_name
from services.messages.interaction import send_interaction_message
from services.logger.client import CustomLogger
from services.cache.client import custom_cache

logger = CustomLogger
bot = get_bot()


class TopUpView(View):
    """
    View special for core command top-up.
    """

    def __init__(
        self, 
        amount: float,
        guild: discord.Guild = None,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        super().__init__(timeout=180)
        self.amount = amount
        self.guild = guild if guild else bot.get_guild(int(MAIN_GUILD_ID))
        self.lang = lang

    async def _get_top_up_url(self, url: str, user: discord.User) -> str:
        self.wallet = await get_server_wallet_by_discord_id(user.id)
        channel = await get_or_create_channel_by_category_and_name(
            category_name=GUIDE_CATEGORY_NAME,
            channel_name=GUIDE_CHANNEL_NAME,
            guild=self.guild
        )
        request_data = {
            "price": str(self.amount),
            "discord_id": str(user.id),
            "wallet_to_pay": self.wallet,
            "challenge_id": "5234e156-f328-4902-a832-815bc90504d5",
            "success_url": channel.jump_url,
            "fail_url": channel.jump_url
        }
        try:
            response = requests.post(url=url, json=request_data, timeout=10)
        except requests.Timeout:
            logger.error(f"Top Up timeount! {url}")
            return None
        if response.status_code != 200:
            logger.http_error("TOP UP", response=response)
            return None
        balance = await get_usdt_balance_by_discord_user(user)
        custom_cache.set_top_up(user.id, balance)
        return response.text
    
    async def _send_message(
        self,
        *,
        url: str,
        interaction: discord.Integration,
        method: str
    ) -> None:
        top_up_response_url = await self._get_top_up_url(
            url=url, user=interaction.user
        )
        message_embed = discord.Embed(
            title=f"🔴 {method} Top up",
            description=translations["top_up_address_message"][self.lang].format(
                method=method,
                wallet=self.wallet
            )
        )
        error_message = translations["server_error_payment"][self.lang]
        await send_interaction_message(
            interaction=interaction,
            message=top_up_response_url,
            embed=discord.Embed(
                description=message_embed if top_up_response_url else error_message,
                title=method
            )
        )

    @discord.ui.button(label="BinancePay", style=discord.ButtonStyle.blurple, row=1)
    async def binance(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "binance",
            interaction=interaction,
            method="Binance"
        )

    @discord.ui.button(label="PayPal", style=discord.ButtonStyle.blurple, row=1)
    async def paypal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "sellix",
            interaction=interaction,
            method="Sellix"
        )

    @discord.ui.button(label="Visa", style=discord.ButtonStyle.blurple, row=2)
    async def visa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "sellix",
            interaction=interaction,
            method="Sellix"
        )

    @discord.ui.button(label="MasterCard", style=discord.ButtonStyle.blurple, row=2)
    async def master_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "sellix",
            interaction=interaction,
            method="Sellix"
        )

    @discord.ui.button(label="Google Pay", style=discord.ButtonStyle.blurple, row=3)
    async def google_pay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "sellix",
            interaction=interaction,
            method="Sellix"
        )

    @discord.ui.button(label="MIR", style=discord.ButtonStyle.blurple, row=3)
    async def freecasa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "free-kassa",
            interaction=interaction,
            method="Freecasa"
        )
