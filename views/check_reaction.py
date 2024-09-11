import datetime
import discord

from config import (
    FIRST_LIMIT_CHECK_MINUTES,
    SECOND_LIMIT_CHECK_MINUTES,
)
from database.dto.psql_reaction import ReactionDTO


class CheckReactionView(discord.ui.View):
    """
    Class for check kicker reaction.
    """

    def __init__(self, *, kicker: discord.User):
        super().__init__(timeout=None)
        self.kicker = kicker
        self.created_at = datetime.datetime.utcnow()

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
        interaction: discord.Integration,
        reaction_seconds: float
    ) -> None:
        text_message: str = ""
        if reaction_seconds < FIRST_LIMIT_CHECK_MINUTES * 60:
            reaction_dto = ReactionDTO()
            await reaction_dto.add_reaction(
                discord_id=interaction.user.id,
                seconds=int(reaction_seconds),
                created_at=self.created_at
            )
            text_message = (
                "Great! You've successfully passed "
                "the availability check. Keep up the "
                "quick responses!"
            )
        elif reaction_seconds < SECOND_LIMIT_CHECK_MINUTES * 60:
            text_message = (
                "Oops! You clicked the button too late. "
                "Remember, quick response times help "
                "ensure a better experience for your clients"
            )
        else:
            text_message = (
                "It looks like you missed the "
                "availability check. Please make "
                "sure to be responsive for a better "
                "service experience"
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


