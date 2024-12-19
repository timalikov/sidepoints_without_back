from dotenv import load_dotenv
from typing import Literal
import os

import discord

from translate import translations
from bot_instance import get_bot

from database.dto.psql_services import Services_Database
from services.view_collector import ViewCollector
from services.messages.interaction import send_interaction_message
from message_constructors import create_profile_embed
from views.base_view import BaseView
from views.share_command_view import ShareCommandView

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))


class Profile_Exist(BaseView):
    def __init__(
        self,
        discord_id,
        user_choice="ALL",
        lang: Literal["ru", "en"] = "en",
        collector: ViewCollector = None
    ):
        super().__init__(timeout=None, collector=collector)
        self.discord_id = discord_id
        self.user_choice = user_choice
        self.no_user = False
        self.no_service = False
        self.service_db = Services_Database()
        self.list_services = []
        self.index = 0
        self.profile_embed = None
        self.affiliate_channel_ids = []  
        self.cooldowns = {}
        self.lang = lang

    async def initialize(self):
        self.list_services = await self.service_db.get_services_by_discordId(self.discord_id)
        is_user_registered = await self.service_db.is_user_registered(discord_id=self.discord_id)
        if not is_user_registered:
            self.no_user = True
            return
        
        if self.list_services:
            for index, service in enumerate(self.list_services):
                service = dict(service)
                service["service_category_name"] = service["tag"]
                self.list_services[index] = service
            self.profile_embed = create_profile_embed(self.list_services[self.index], lang=self.lang)
            self.affiliate_channel_ids = await self.service_db.get_channel_ids()
        else:
            self.no_service = True



    @discord.ui.button(label="Edit", style=discord.ButtonStyle.success, custom_id="profile_edit")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile_edit", 
            interaction.guild.id if interaction.guild else None
        )

        payment_link = f"{os.getenv('WEB_APP_URL')}/services/{self.list_services[self.index]['service_id']}/edit?side_auth=DISCORD"
        await send_interaction_message(interaction=interaction, message=translations["edit_service_link"][self.lang].format(link=payment_link))

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
            service["service_category_name"] = service["tag"]
            self.list_services[index] = service
        self.profile_embed = create_profile_embed(self.list_services[self.index], lang=self.lang)
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="profile_share")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile_share", 
            interaction.guild.id if interaction.guild else None
        )
        share_command_view = ShareCommandView(
            bot,
            self.list_services,
            self.index,
            self.affiliate_channel_ids,
            lang=self.lang
        )
        await share_command_view.share(interaction)

    @discord.ui.button(label="Create a new service", style=discord.ButtonStyle.secondary, custom_id="create_service")
    async def create_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile_create_service", 
            interaction.guild.id if interaction.guild else None
        )
        payment_link = f"{os.getenv('WEB_APP_URL')}/services/create?side_auth=DISCORD"
        await interaction.followup.send(translations["create_service_link"][self.lang].format(link=payment_link), ephemeral=True)
