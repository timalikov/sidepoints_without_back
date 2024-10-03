from typing import Literal

import datetime
import discord

from config import (
    FIRST_LIMIT_CHECK_MINUTES,
    SECOND_LIMIT_CHECK_MINUTES,
)
from database.dto.psql_reaction import ReactionDTO
from translate import translations


class CheckReactionView(discord.ui.View):
    """
    Class for check kicker reaction.
    """

    def __init__(self, *, kicker: discord.User, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.kicker = kicker
        self.created_at = datetime.datetime.utcnow()
        self.lang = lang

    def _get_kwargs_for_send_message(
        self,
        *,
        text: str,
        title: str = None,
    ) -> dict:
        return {
            "view": None,
            "embed": discord.Embed(title=title, description=text)
        }

    async def send_message_and_save_data(
        self,
        interaction: discord.Interaction,
        reaction_seconds: float
    ) -> None:
        reaction_time: int = None
        text_message: str = ""
        reaction_dto = ReactionDTO()
        if reaction_seconds < FIRST_LIMIT_CHECK_MINUTES * 1:
            reaction_time = int(reaction_seconds)
            text_message = translations["success_check"][self.lang]
        elif reaction_seconds < SECOND_LIMIT_CHECK_MINUTES * 1:
            reaction_time = int(reaction_seconds)
            text_message = translations["late_response"][self.lang]
        else:
            text_message = translations["missed_check"][self.lang]

        await reaction_dto.add_reaction(
            discord_id=interaction.user.id,
            seconds=reaction_time,
            created_at=self.created_at
        )
        kwargs = self._get_kwargs_for_send_message(
            text=text_message
        )
        await interaction.response.edit_message(**kwargs)

    @discord.ui.button(label="Check", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        pressed_at = datetime.datetime.utcnow()
        reaction_seconds: int = (pressed_at - self.created_at).total_seconds()
        await self.send_message_and_save_data(interaction=interaction, reaction_seconds=reaction_seconds)
