from typing import Literal, List

import discord

from translate import translations
from bot_instance import get_bot

from models.payment import get_usdt_balance_by_discord_user
from services.messages.interaction import send_interaction_message
from services.logger.client import CustomLogger
from views.top_up_view import TopUpView

logger = CustomLogger
bot = get_bot()


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
        view = TopUpView(
            amount=self.values[0],
            guild=interaction.guild,
            lang=self.lang
        )
        balance = await get_usdt_balance_by_discord_user(interaction.user)
        await send_interaction_message(
            interaction=interaction,
            view=view,
            embed=discord.Embed(
                description=translations["top_up_message"][self.lang].format(balance=balance),
                title=translations["top_up_balance"][self.lang]
            )
        )
