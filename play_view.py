import discord
from discord.ui import View

import os
from dotenv import load_dotenv

from config import APP_CHOICES, MAIN_GUILD_ID, FORUM_NAME
from services.kicker_sort_service import KickerSortingService
from services.messages.interaction import send_interaction_message
from message_constructors import create_profile_embed
from bot_instance import get_bot
from models.forum import find_forum
from database.dto.sql_profile import log_to_database
from database.dto.psql_services import Services_Database
from database.dto.sql_forum_posted import ForumUserPostDatabase

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES

class PlayView(View):
    @classmethod
    async def create(cls, user_choice="ALL", username=None):
        services_db = Services_Database(app_choice=user_choice)
        instance = cls(None, services_db)
        
        instance.services_db = services_db
        instance.kicker_manager = KickerSortingService(services_db)

        if username:
            service = await services_db.get_services_by_username(username)
        else:
            service = await instance.kicker_manager.fetch_first_service()

        if service:
            instance.set_service(service)
        else:
            instance.no_user = True

        return instance 
    
    def __init__(self, service: dict = None, services_db: Services_Database = None):
        super().__init__(timeout=None)
        self.service = service
        self.services_db = services_db
        self.no_user = False  
        self.sorted_kickers = []  
        self.current_kicker_index = 0
        self.profile_embed = None
        self.kicker_manager = None

    def set_service(self, service):
        """
        Helper function to set the service and create the embed.
        """
        self.service = service
        self.profile_embed = create_profile_embed(service)
        self.no_user = False  

    async def is_member_of_main_guild(self, user_id):
        main_guild = bot.get_guild(main_guild_id)
        if main_guild is None:
            return False
        member = main_guild.get_member(user_id)
        return member is not None

    @discord.ui.button(label="Go", style=discord.ButtonStyle.success, custom_id="play_user")
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        is_member = await self.is_member_of_main_guild(interaction.user.id)
        if not is_member:
            await interaction.followup.send("Please join the server before proceeding: https://discord.gg/sidekick", ephemeral=True)
            return

        await log_to_database(interaction.user.id, "play_user")
        serviceId = self.service['service_id']
        discordServerId = interaction.guild.id if interaction.guild else MAIN_GUILD_ID
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{serviceId}?discordServerId={discordServerId}&side_auth=DISCORD"
        await interaction.followup.send(f"To participate in this session, please complete your payment here: {payment_link}", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_user")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "next_user")
        next_service = await self.kicker_manager.get_next_valid_service()
        if next_service:
            self.set_service(next_service)
            await interaction.edit_original_response(embed=self.profile_embed, view=self)
        else:
            await interaction.followup.send("No more valid players found.", ephemeral=True)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_profile")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        user_id = self.service['discord_id']
        forum = await find_forum(guild=interaction.guild, forum_name=FORUM_NAME)
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, main_guild_id)

        message: str = ""
        if thread_id:
            thread = forum.get_thread(int(thread_id))
            if not thread:
                message = "Profile not found!"
            else:
                message = f"Profile account: {thread.jump_url}"
        else:
            message = "The SideKicker account is not posted yet, please wait or you can share the username."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    @discord.ui.button(label="Chat", style=discord.ButtonStyle.secondary, custom_id="chat_user")
    async def chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "chat_user")
        user_id = self.service['discord_id']
        member = interaction.guild.get_member(int(user_id))
        if member:
            chat_link = f"Trial chat with the Kicker: <@!{int(user_id)}>"
            if interaction.response.is_done():
                await interaction.followup.send(f"{chat_link}", ephemeral=True)
            else:
                await interaction.response.send_message(f"{chat_link}", ephemeral=True)
        else:
            chat_link = f"Click below to connect with user https://discord.com/users/{user_id}"
            if interaction.response.is_done():
                await interaction.followup.send(f"Chat with the user: {chat_link}", ephemeral=True)
            else:
                await interaction.followup.send(f"Chat with the user: {chat_link}", ephemeral=True)

    @discord.ui.button(label="Boost", style=discord.ButtonStyle.success, custom_id="boost_user")
    async def boost(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if self.service:
            payment_link = f"{os.getenv('WEB_APP_URL')}/boost/{self.service['profile_id']}?side_auth=DISCORD"
            await send_interaction_message(interaction=interaction, message=f"To boost the profile go to the link below: {payment_link}")
        else:
            await send_interaction_message(interaction=interaction, message="No user found to boost.")
            print(f"Boost button clicked, but no service found for user {interaction.user.id}")