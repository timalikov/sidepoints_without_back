import discord
# from sql_challenge import SQLChallengeDatabase  # Adjusted import to use SQLChallengeDatabase
from sql_forum_posted import ForumUserPostDatabase
# from sql_profile import Profile_Database
from discord.ui import View
# from datetime import datetime
from config import APP_CHOICES, HOST_PSQL, USER_PSQL, PASSWORD_PSQL, DATABASE_PSQL
from dotenv import load_dotenv
from message_constructors import create_profile_embed_2
import os
from bot_instance import get_bot
from getServices import DiscordServiceFetcher
from sql_profile import log_to_database
from database.psql_services import Services_Database

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES


class Profile_Exist(View):
    def __init__(self, discord_id, user_choice="ALL"):
        super().__init__(timeout=None)
        self.discord_id = discord_id
        self.user_choice = user_choice
        self.no_user = False
        self.service_db = Services_Database()
        self.list_services = []
        self.index = 0
        self.profile_embed = None

    async def initialize(self):
        self.list_services = await self.service_db.get_services_by_discord_id(self.discord_id)
        if self.list_services:
            self.profile_embed = create_profile_embed_2(self.list_services[self.index])
        else:
            self.no_user = True


    @discord.ui.button(label="Edit", style=discord.ButtonStyle.success, custom_id="edit_service")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "edit_service")

        payment_link = f"https://app.sidekick.fans/services/{self.list_services[self.index]['service_id']}/edit"
        await interaction.followup.send(f"To edit your service go to the link below: {payment_link}", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_user")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "next_user")
        if self.index < len(self.list_services) - 1:
            self.index += 1
        else:
            self.index = 0

        self.profile_embed = create_profile_embed_2(self.list_services[self.index])
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_profile")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        user_id = self.list_services[self.index]["discord_id"]
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, str(main_guild_id))

        if thread_id:
            thread = await bot.fetch_channel(int(thread_id))
            profile_link = thread.jump_url
            if interaction.response.is_done():
                await interaction.followup.send(f"Profile account: {profile_link}", ephemeral=True)
            else:
                await interaction.response.send_message(f"Profile account: {profile_link}", ephemeral=True)
        else:
            if interaction.response.is_done():
                await interaction.followup.send("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)
            else:
                await interaction.response.send_message("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)

    @discord.ui.button(label="Create a new service", style=discord.ButtonStyle.secondary, custom_id="create_service")
    async def create_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "create_service")
        payment_link = "https://app.sidekick.fans/services/create"
        await interaction.followup.send(f"To create a new service go to the link below: {payment_link}", ephemeral=True)
