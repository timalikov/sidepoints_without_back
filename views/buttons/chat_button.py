from typing import Literal, Dict

import discord

from bot_instance import get_bot
from translate import translations

from views.buttons.base_button import BaseButton
from database.dto.psql_services import Services_Database

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
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "chat_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        user_id = self.view.service['discord_id']
        try:
            member = interaction.guild.get_member(int(user_id))
        except AttributeError:
            member = None
        except ValueError as e:
            print(f"CHAT ERROR: {e}")
            member = None
        if member:
            chat_link = translations["trial_chat_with_kicker"][self.lang].format(user_id=user_id)
            if interaction.response.is_done():
                await interaction.followup.send(chat_link, ephemeral=True)
            else:
                await interaction.response.send_message(chat_link, ephemeral=True)
        else:
            chat_link = translations["connect_with_user"][self.lang].format(user_id=user_id)
            await interaction.followup.send(
                translations["connect_with_user"][self.lang].format(user_id=user_id),
                ephemeral=True
            )
