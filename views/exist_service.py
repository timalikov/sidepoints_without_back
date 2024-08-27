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
from views.share_view import ShareView

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
        await log_to_database(interaction.user.id, "edit_service")

        payment_link = f"{os.getenv('WEB_APP_URL')}/services/{self.list_services[self.index]['service_id']}/edit"
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
        username = self.list_services[self.index]["profile_username"]
        service_description = self.list_services[self.index]["service_description"]
        category = self.list_services[self.index]["service_type_name"]
        price = self.list_services[self.index]["service_price"]
        service_image = self.list_services[self.index].get("service_image", None)  
        service_id = self.list_services[self.index]["service_id"]
        discord_server_id = interaction.guild.id
        
        channel_ids = self.affiliate_channel_ids

        embed = discord.Embed(
            title=f"Username: {username}",
            description=f"**Description:** {service_description}\n**Category:** {category}\n**Price:** ${price}"
        )
        if service_image:
            embed.set_image(url=service_image) 

        share_view = ShareView(user_id=user_id, service_id=service_id, discord_server_id=discord_server_id)

        for record in channel_ids:
            channel_id = record["channel_id"]
            channel = await bot.fetch_channel(channel_id)
            if channel:
                try:
                    await channel.send(embed=embed, view=share_view)
                except Exception as e:
                    print(f"Failed to send message to channel {channel_id}: {e}")

        message = "Message has been shared across all affiliate channels."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    @discord.ui.button(label="Create a new service", style=discord.ButtonStyle.secondary, custom_id="create_service")
    async def create_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "create_service")
        payment_link = "{os.getenv('WEB_APP_URL')}/services/create"
        await interaction.followup.send(f"To create a new service go to the link below: {payment_link}", ephemeral=True)