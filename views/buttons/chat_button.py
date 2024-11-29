from typing import Literal, Dict

import discord

from bot_instance import get_bot
from translate import translations

from views.buttons.base_button import BaseButton
from database.dto.psql_services import Services_Database
from services.messages.interaction import send_interaction_message

bot = get_bot()


class ChatButton(BaseButton):
    def __init__(
        self,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Chat",
            style=discord.ButtonStyle.primary,
            custom_id="chat",
            row=row,
            emoji="💬"
        )
        self.lang = lang
        self._view_variables = ["service"]

    async def callback(self, interaction: discord.Interaction):
        await Services_Database().log_to_database(
            interaction.user.id, 
            "chat_kicker", 
            interaction.guild.id if interaction.guild else None
        )
        try:
            user_id = int(self.view.service['discord_id'])
            username = self.view.service['profile_username']
            chat_message = (
                f'{translations["connect_chat_link"][self.lang].format(user_id=user_id)}\n'
                f'{translations["chat_dm"][self.lang].format(username=username, user_id=user_id)}'
            )
        except (AttributeError, TypeError):
            chat_message = translations["chat_dm_kicker_id_is_broken"][self.lang]
        await send_interaction_message(
            interaction=interaction,
            message=chat_message
        )