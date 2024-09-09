import discord
from sql_forum_posted import ForumUserPostDatabase
from discord.ui import View
from config import MAIN_GUILD_ID, FORUM_ID, APP_CHOICES, LEADER_BOT_CHANNEL, CATEGORY_TO_TAG, FORUM_ID_LIST, LEADER_BOT_CHANNEL_LIST
from dotenv import load_dotenv
from message_constructors import create_profile_embed
import os
from bot_instance import get_bot
from sql_profile import log_to_database
from database.psql_services import Services_Database

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES


class PlayView(View):

    @classmethod
    async def create(cls, user_choice="ALL", username=None):
        services_db = Services_Database(app_choice=user_choice)
        if username:
            service = await services_db.get_services_by_username(username)
        else:
            service = await services_db.get_next_service()

        if service:
            service["service_category_name"] = await services_db.get_service_category_name(service["service_type_id"])

        return cls(service, services_db)
    
    def __init__(self, service: dict = None, services_db: Services_Database = None):
        super().__init__(timeout=None)
        self.service = service
        self.services_db = services_db
        self.no_user = False
        if self.service:
            self.profile_embed = create_profile_embed(service)
        else:
            self.no_user = True

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
        discordServerId = interaction.guild.id
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{serviceId}?discordServerId={discordServerId}"
        await interaction.followup.send(f"To participate in this session, please complete your payment here: {payment_link}", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_user")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "next_user")
        self.service = await self.services_db.get_next_service()
        if self.service:
            self.service["service_category_name"] = await self.services_db.get_service_category_name(self.service["service_type_id"])
        self.profile_embed = create_profile_embed(self.service)
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_profile")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        user_id = self.service['discord_id']
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, str(main_guild_id))

        if thread_id:
            thread = await bot.fetch_channel(int(thread_id))
            profile_link = thread.jump_url
            # profile_link = f"https://discord.com/channels/{main_guild_id}/{thread_id}"
            if interaction.response.is_done():
                await interaction.followup.send(f"Profile account: {profile_link}", ephemeral=True)
            else:
                await interaction.response.send_message(f"Profile account: {profile_link}", ephemeral=True)
        else:
            if interaction.response.is_done():
                await interaction.followup.send("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)
            else:
                await interaction.response.send_message("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)

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
