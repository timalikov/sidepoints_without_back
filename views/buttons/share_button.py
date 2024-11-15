from typing import Literal, Dict

import discord

from bot_instance import get_bot
from translate import translations
from config import FORUM_NAME

from models.forum import find_forum
from database.dto.psql_services import Services_Database
from database.dto.sql_forum_posted import ForumUserPostDatabase
from views.buttons.base_button import BaseButton

bot = get_bot()


class ShareButton(BaseButton):
    def __init__(
        self,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(label="Share", style=discord.ButtonStyle.primary, custom_id="share", row=row)
        self.lang = lang
        self._view_variables = ["service"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "share_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        user_id = self.view.service['discord_id']
        forum = await find_forum(guild=interaction.guild, forum_name=FORUM_NAME)
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, interaction.guild.id)

        message: str = ""
        if thread_id:
            try:
                thread = forum.get_thread(int(thread_id))
            except ValueError as e:
                print("Play View SHARE ERROR: {e}")
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
