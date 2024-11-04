from typing import Literal, List

import discord
from discord.ui import View
import requests

from config import TOP_UP_URL
from translate import translations

from models.payment import get_server_wallet_by_discord_id, get_usdt_balance_by_discord_user
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

    async def _get_top_up_url(self, url: str, user: discord.User) -> str:
        self.wallet = await get_server_wallet_by_discord_id(user.id)
        request_data = {
            "price": str(self.amount),
            "discord_id": str(user.id),
            "wallet_to_pay": self.wallet,
            "challenge_id": "5234e156-f328-4902-a832-815bc90504d5",
            "success_url": "https://apptest.sidekick.fans/topup/?topup_status=success",
            "fail_url": "https://apptest.sidekick.fans/topup/?topup_status=fail"
        }
        response = requests.post(url=url, json=request_data)
        if response.status_code != 200:
            logger.http_error("TOP UP", response=response)
            return None
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


    @discord.ui.button(label="OpBNB OnChain transfer", style=discord.ButtonStyle.blurple, row=1)
    async def opbnb(self, interaction: discord.Interaction, button: discord.ui.Button):
        wallet = await get_server_wallet_by_discord_id(interaction.user.id)
        await send_interaction_message(
            interaction=interaction,
            embed=discord.Embed(
                description=translations["opbnb_balance_message"][self.lang].format(wallet=wallet),
                title="OnChain transfer"
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

    @discord.ui.button(label="Visa", style=discord.ButtonStyle.blurple, row=2)
    async def visa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "sellix",
            interaction=interaction,
            method="Sellix"
        )

    @discord.ui.button(label="Master Card", style=discord.ButtonStyle.blurple, row=2)
    async def master_card(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "sellix",
            interaction=interaction,
            method="Sellix"
        )

    @discord.ui.button(label="PayPal", style=discord.ButtonStyle.blurple, row=2)
    async def paypal(self, interaction: discord.Interaction, button: discord.ui.Button):
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

    @discord.ui.button(label="Freecasa (Mir)", style=discord.ButtonStyle.blurple, row=3)
    async def freecasa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._send_message(
            url=TOP_UP_URL + "free-kassa",
            interaction=interaction,
            method="Freecasa"
        )


class TopUpDropdownMenu(discord.ui.Select):
    def __init__(self, *, lang: Literal["en", "ru"] = "en"):
        _amounts: List[int] = [1, 5, 10, 20, 30, 50, 70, 100]
        options = [
            discord.SelectOption(label=str(amount), description=f"Top up {amount} usdt")
            for amount in _amounts
        ]
        self.lang = lang
        super().__init__(placeholder="Select amount...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        view = TopUpView(amount=self.values[0], lang=self.lang)
        balance = await get_usdt_balance_by_discord_user(interaction.user)
        await send_interaction_message(
            interaction=interaction,
            view=view,
            embed=discord.Embed(
                description=translations["top_up_message"][self.lang].format(balance=balance),
                title=translations["top_up_balance"][self.lang]
            )
        )
