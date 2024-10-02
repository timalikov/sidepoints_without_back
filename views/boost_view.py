import discord
# from database.dto.sql_challenge import SQLChallengeDatabase  # Adjusted import to use SQLChallengeDatabase
from database.dto.sql_forum_posted import ForumUserPostDatabase
# from database.dto.sql_profile import Profile_Database
from discord.ui import View
# from datetime import datetime
from config import APP_CHOICES, FORUM_NAME
from dotenv import load_dotenv
from message_constructors import create_profile_embed_2
import os
from bot_instance import get_bot
from models.forum import find_forum
from database.dto.sql_profile import log_to_database
from database.dto.psql_services import Services_Database

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES


class BoostView(View):
    def __init__(self, user_name):
        super().__init__(timeout=None)
        self.user_name = user_name
        self.no_user = False
        self.service_db = Services_Database(user_name=self.user_name)
        self.user_data = None
        self.index = 0
        self.profile_embed = None

    async def initialize(self):
        self.user_data = await self.service_db.get_next_service()
        if self.user_data:
            self.profile_embed = create_profile_embed_2(self.user_data)
        else:
            self.no_user = True


    @discord.ui.button(label="Boost", style=discord.ButtonStyle.success, custom_id="boost")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # await Services_Database().log_to_database(
        #     interaction.user.id, 
        #     "boost", 
        #     interaction.guild.id if interaction.guild else None
        # )

        payment_link = f"{os.getenv('WEB_APP_URL')}/boost/{self.user_data['profile_id']}?side_auth=DISCORD"
        await interaction.followup.send(f"To boost the profile go to the link below: {payment_link}", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_kicker")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # await Services_Database().log_to_database(
        #     interaction.user.id, 
        #     "next_kicker", 
        #     interaction.guild.id if interaction.guild else None
        # )

        self.user_data = await self.service_db.get_next_service()

        self.profile_embed = create_profile_embed_2(self.user_data)
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_kicker")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # await Services_Database().log_to_database(
        #     interaction.user.id, 
        #     "share_kicker", 
        #     interaction.guild.id if interaction.guild else None
        # )

        user_id = self.user_data['discord_id']
        forum = await find_forum(guild=interaction.guild, forum_name=FORUM_NAME)
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, str(main_guild_id))

        if thread_id:
            thread = forum.get_thread(int(thread_id))
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


    # @discord.ui.button(label="Create a new service", style=discord.ButtonStyle.secondary, custom_id="create_service")
    # async def create_service(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.defer(ephemeral=True)
    #     await log_to_database(interaction.user.id, "create_service")
    #     payment_link = "{os.getenv('WEB_APP_URL')}/services/create"
    #     await interaction.followup.send(f"To create a new service go to the link below: {payment_link}", ephemeral=True)
