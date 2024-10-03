from typing import Literal
import os
from dotenv import load_dotenv

import discord
from discord.ui import View

from bot_instance import get_bot
from config import APP_CHOICES, FORUM_NAME
from translate import translations

from database.dto.sql_forum_posted import ForumUserPostDatabase
from message_constructors import create_profile_embed_2
from models.forum import find_forum
from database.dto.sql_profile import log_to_database
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
            self.profile_embed = create_profile_embed_2(self.user_data, lang=self.lang)
        else:
            self.no_user = True

    @discord.ui.button(label="Boost", style=discord.ButtonStyle.success, custom_id="edit_service")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "edit_service")

        payment_link = f"{os.getenv('WEB_APP_URL')}/boost/{self.user_data['profile_id']}?side_auth=DISCORD"
        await interaction.followup.send(
            translations["boost_profile_link"][interaction.user.lang].format(payment_link=payment_link), 
            ephemeral=True
        )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_user")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await log_to_database(interaction.user.id, "next_user")

        self.user_data = await self.service_db.get_next_service()

        self.profile_embed = create_profile_embed_2(self.user_data, lang=self.lang)
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_profile")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        user_id = self.user_data['discord_id']
        forum = await find_forum(guild=interaction.guild, forum_name=FORUM_NAME)
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, str(main_guild_id))

        if thread_id:
            thread = forum.get_thread(int(thread_id))
            profile_link = thread.jump_url
            if interaction.response.is_done():
                await interaction.followup.send(
                    translations["profile_account"][interaction.user.lang].format(profile_link=profile_link), 
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    translations["profile_account"][interaction.user.lang].format(profile_link=profile_link), 
                    ephemeral=True
                )
        else:
            if interaction.response.is_done():
                await interaction.followup.send(
                    translations["sidekicker_account_not_posted"][interaction.user.lang], 
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    translations["sidekicker_account_not_posted"][interaction.user.lang], 
                    ephemeral=True
                )
