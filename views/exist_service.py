import discord
from discord.ui import View
from config import APP_CHOICES, HOST_PSQL, USER_PSQL, PASSWORD_PSQL, DATABASE_PSQL
from dotenv import load_dotenv
from message_constructors import create_profile_embed_2
import os
from bot_instance import get_bot
from sql_profile import log_to_database
from database.psql_services import Services_Database
from views.share_command_view import ShareCommandView
from background_tasks import create_private_discord_channel

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
        self.affiliate_channel_ids = []  
        self.cooldowns = {}

    async def initialize(self):
        self.list_services = await self.service_db.get_services_by_discordId(self.discord_id)
        if self.list_services:
            self.profile_embed = create_profile_embed_2(self.list_services[self.index])
            self.affiliate_channel_ids = await self.service_db.get_channel_ids()
        else:
            self.no_user = True


    @discord.ui.button(label="Edit", style=discord.ButtonStyle.success, custom_id="edit_service")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        guild_id = main_guild_id
        guild = bot.get_guild(guild_id)
        channel_name = f"private-channel-{self.list_services[self.index]['profile_username']}"
        challenger = guild.get_member(836655813048402011)
        challenged = guild.get_member(1278392054983954433)
        serviceName = self.list_services[self.index]["service_description"]
        kickerUsername = self.list_services[self.index]['profile_username']
        success, channel = await create_private_discord_channel(bot, guild_id, channel_name, challenger, challenged, serviceName, kickerUsername)
        if not success:
                return False, "Failed to create a new private channel"
        
        # await log_to_database(interaction.user.id, "edit_service")

        # payment_link = f"{os.getenv('WEB_APP_URL')}/services/{self.list_services[self.index]['service_id']}/edit"
        # await interaction.followup.send(f"To edit your service go to the link below: {payment_link}", ephemeral=True)

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
        share_command_view = ShareCommandView(bot, self.list_services, self.index, self.affiliate_channel_ids)
        await share_command_view.share(interaction)


    @discord.ui.button(label="Create a new service", style=discord.ButtonStyle.secondary, custom_id="create_service")
    async def create_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "create_service")
        payment_link = f"{os.getenv('WEB_APP_URL')}/services/create"
        await interaction.followup.send(f"To create a new service go to the link below: {payment_link}", ephemeral=True)