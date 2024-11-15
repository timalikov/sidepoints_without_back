import discord
from discord import app_commands

from discord.ext import commands
from translate import get_lang_prefix, translations
from views.dropdown.top_up_dropdown import TopUpDropdownMenu
from models.payment import (
    get_server_wallet_by_discord_id,
)
from web3_interaction.balance_checker import get_usdt_balance
from services.messages.interaction import send_interaction_message
from bot_instance import get_bot

bot = get_bot()


class WalletCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="wallet",
        description="Use this command to access your wallet."
    )
    async def wallet(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild_id = interaction.guild_id if interaction.guild_id else None
        lang = get_lang_prefix(guild_id)
        
        wallet = await get_server_wallet_by_discord_id(user_id=interaction.user.id)
        balance = get_usdt_balance(wallet) if wallet else 0
        
        message = translations["wallet_balance_message"][lang].format(
            balance=balance, wallet=wallet
        )
        dropdown = TopUpDropdownMenu(lang=lang)
        view = discord.ui.View(timeout=None)
        view.add_item(dropdown)
        
        await send_interaction_message(
            interaction=interaction,
            embed=discord.Embed(
                description=message,
                title=translations["wallet_title"][lang],
                colour=discord.Colour.orange()
            ),
            view=view
        )

