from typing import Literal
import os
from dotenv import load_dotenv

import discord
from discord.ui import View

from bot_instance import get_bot
from config import APP_CHOICES, FORUM_NAME
from translate import translations

from database.dto.sql_forum_posted import ForumUserPostDatabase
from message_constructors import create_profile_embed
from models.forum import find_forum
from database.dto.psql_services import Services_Database

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES


class BoostView(View):
    def __init__(self, user_name, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.user_name = user_name
        self.no_user = False
        self.service_db = Services_Database(user_name=self.user_name)
        self.user_data = None
        self.index = 0
        self.profile_embed = None
        self.lang = lang

    async def initialize(self):
        self.user_data = await self.service_db.get_next_service()
        if self.user_data:
            self.profile_embed = create_profile_embed(self.user_data, lang=self.lang)
        else:
            self.no_user = True


    @discord.ui.button(label="Boost", style=discord.ButtonStyle.success, custom_id="boost")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "boost", 
            interaction.guild.id if interaction.guild else None
        )

        payment_link = f"{os.getenv('WEB_APP_URL')}/boost/{self.user_data['profile_id']}?side_auth=DISCORD"
        await interaction.followup.send(
            translations["boost_profile_link"][self.lang].format(boost_link=payment_link), 
            ephemeral=True
        )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_kicker")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "next_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        self.user_data = await self.service_db.get_next_service()

        self.profile_embed = create_profile_embed(self.user_data, lang=self.lang)
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_kicker")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "share_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        user_id = self.user_data['discord_id']
        forum = await find_forum(guild=interaction.guild, forum_name=FORUM_NAME)
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, interaction.guild.id)

        message: str = ""
        if thread_id:
            try:
                thread = forum.get_thread(int(thread_id))
            except ValueError as e:
                print(f"SHARE ERROR: {e}")
                thread = None
            if not thread:
                message = translations["profile_not_found"][self.lang]
            else:
                message = (
                    translations["share_profile_account"][self.lang]
                    .format(profile_link=thread.jump_url)
                )
        else:
            message = translations["sidekicker_account_not_posted"][self.lang]
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
