import discord

from database.psql_wallets import Wallets_Database
from sql_forum_posted import ForumUserPostDatabase
from discord.ui import View
from config import APP_CHOICES
from dotenv import load_dotenv
from message_constructors import create_profile_embed_2
import os
from bot_instance import get_bot
from sql_profile import log_to_database
from database.psql_services import Services_Database
from web3_interaction.balance_checker import get_usdt_balance

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES

class Wallet_exist(View):
    def __init__(self, discord_id = "random id", wallet_id = "random id"):
        super().__init__(timeout=None)
    @discord.ui.button(label="Wallet", style=discord.ButtonStyle.success, custom_id="wallet_button")
    async def wallet_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "wallet_button")
        await interaction.followup.send(f"Press the link to get access to the wallet: {os.getenv('WEB_APP_URL')}/manage", ephemeral=True)

    @discord.ui.button(label="Top up", style=discord.ButtonStyle.primary, custom_id="top_up_button")
    async def top_up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "top_up_button")
        await interaction.followup.send("Press the link to get access to the top up: {os.getenv('WEB_APP_URL')}/topup", ephemeral=True)

    @discord.ui.button(label="Balance", style=discord.ButtonStyle.secondary, custom_id="balance_button")
    async def balance_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "balance_button")
        wallet_obj = Wallets_Database()
        wallet_address = await wallet_obj.get_wallet_by_discord_id(str(interaction.user.id))
        # wallet_address = await wallet_obj.get_wallet_by_discord_id('930005621728763904')
        if wallet_address:
            balance_value = get_usdt_balance(wallet_address)
            await interaction.followup.send(f"Your balance: {balance_value} USDT", ephemeral=True)
        else:
            await interaction.followup.send(f"Please create a crypto-wallet connected to your discord account via link: {os.getenv('WEB_APP_URL')}/manage", ephemeral=True)

