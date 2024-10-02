import discord
from discord.ui import View
from config import APP_CHOICES
from dotenv import load_dotenv
from message_constructors import create_profile_embed
import os
from bot_instance import get_bot
from database.dto.sql_profile import log_to_database
from database.dto.psql_services import Services_Database
from views.share_command_view import ShareCommandView

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
            for index, service in enumerate(self.list_services):
                service = dict(service)
                service["service_category_name"] = await self.service_db.get_service_category_name(service["service_type_id"])
                self.list_services[index] = service
            self.profile_embed = create_profile_embed(self.list_services[self.index])
            self.affiliate_channel_ids = await self.service_db.get_channel_ids()
        else:
            self.no_user = True



    @discord.ui.button(label="Edit", style=discord.ButtonStyle.success, custom_id="profile_edit")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile_edit", 
            interaction.guild.id if interaction.guild else None
        )

        payment_link = f"{os.getenv('WEB_APP_URL')}/services/{self.list_services[self.index]['service_id']}/edit?side_auth=DISCORD"
        await interaction.followup.send(f"To edit your service go to the link below: {payment_link}", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="profile_next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile_next", 
            interaction.guild.id if interaction.guild else None
        )
        if self.index < len(self.list_services) - 1:
            self.index += 1
        else:
            self.index = 0

        for index, service in enumerate(self.list_services):
            service = dict(service)
            service["service_category_name"] = await self.service_db.get_service_category_name(service["service_type_id"])
            self.list_services[index] = service
        self.profile_embed = create_profile_embed(self.list_services[self.index])
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="profile_share")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile_share", 
            interaction.guild.id if interaction.guild else None
        )
        share_command_view = ShareCommandView(bot, self.list_services, self.index, self.affiliate_channel_ids)
        await share_command_view.share(interaction)


    @discord.ui.button(label="Create a new service", style=discord.ButtonStyle.secondary, custom_id="profile_create_service")
    async def create_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile_create_service", 
            interaction.guild.id if interaction.guild else None
        )
        payment_link = f"{os.getenv('WEB_APP_URL')}/services/create?side_auth=DISCORD"
        await interaction.followup.send(f"To create a new service go to the link below: {payment_link}", ephemeral=True)