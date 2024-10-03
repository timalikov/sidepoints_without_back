from dotenv import load_dotenv
import os

import discord
from discord.ui import View

from config import APP_CHOICES
from bot_instance import get_bot
from translate import translations

from database.dto.psql_wallets import Wallets_Database
from database.dto.sql_profile import log_to_database
from web3_interaction.balance_checker import get_usdt_balance

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES

class Wallet_exist(View):
    def __init__(self, discord_id="random id", wallet_id="random id", lang="en"):
        super().__init__(timeout=None)
        self.lang = lang

    @discord.ui.button(label="Wallet", style=discord.ButtonStyle.success, custom_id="wallet_button")
    async def wallet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "wallet_button")
        url = f"{os.getenv('WEB_APP_URL')}/manage?side_auth=DISCORD"
        message = translations["press_wallet_link"][self.lang].format(url=url)
        await interaction.followup.send(message, ephemeral=True)

    @discord.ui.button(label="Top up", style=discord.ButtonStyle.primary, custom_id="top_up_button")
    async def top_up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "top_up_button")
        url = f"{os.getenv('WEB_APP_URL')}/topup?side_auth=DISCORD"
        message = translations["press_top_up_link"][self.lang].format(url=url)
        await interaction.followup.send(message, ephemeral=True)

    @discord.ui.button(label="Balance", style=discord.ButtonStyle.secondary, custom_id="balance_button")
    async def balance_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "balance_button")
        wallet_obj = Wallets_Database()
        wallet_address = await wallet_obj.get_wallet_by_discord_id(str(interaction.user.id))
        
        if wallet_address:
            balance_value = get_usdt_balance(wallet_address)
            message = translations["your_balance"][self.lang].format(balance=balance_value)
            await interaction.followup.send(message, ephemeral=True)
        else:
            url = f"{os.getenv('WEB_APP_URL')}/manage?side_auth=DISCORD"
            message = translations["create_wallet_prompt"][self.lang].format(url=url)
            await interaction.followup.send(message, ephemeral=True)
