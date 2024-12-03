from typing import Literal, Dict

import discord

from bot_instance import get_bot
from config import MAIN_GUILD_ID
from translate import translations

from services.messages.interaction import send_interaction_message
from services.logger.client import CustomLogger
from views.buttons.base_button import BaseButton
from views.dropdown.boost_dropdown import BoostDropdownMenu
from database.dto.psql_services import Services_Database

logger = CustomLogger
bot = get_bot()


class BoostButton(BaseButton):
    def __init__(
        self,
        show_dropdown: bool = False,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Boost",
            style=discord.ButtonStyle.primary,
            custom_id="boost",
            row=row,
            emoji="🚀"
        )
        self.lang = lang
        self.show_dropdown = show_dropdown
        self._view_variables = ["service", "boost_amount"]

    async def with_dropdown(self, interaction: discord.Interaction) -> None:
        if self.view.service:
            dropdown = BoostDropdownMenu(target_service=self.view.service, need_send_boost=True, lang=self.lang)
            view = discord.ui.View(timeout=None)
            view.add_item(dropdown)
            await send_interaction_message(
                interaction=interaction,
                view=view
            )
        else:
            await send_interaction_message(
                interaction=interaction,
                message=translations["no_user_found_to_boost"][self.lang]
            )
            await logger.error_discord(f"Boost button clicked, but no service found for user {interaction.user.id}")

    async def without_dropdown(self, interaction: discord.Interaction) -> None:
        if not self.view.boost_amount:
            await send_interaction_message(
                interaction=interaction,
                embed=discord.Embed(
                    title="Please choose boost amount first!",
                    description="Just one step before you will be able to boost kicker",
                    colour=discord.Colour.dark_red()
                )
            )
            return
        message_kwargs = await BoostDropdownMenu.send_boost_and_get_message(
            user=interaction.user,
            target_service=self.view.service,
            amount=self.view.boost_amount,
            guild=interaction.guild if interaction.guild else bot.get_guild(MAIN_GUILD_ID),
            lang=self.lang
        )
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )
        self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "boost", 
            interaction.guild.id if interaction.guild else None
        )
        if self.show_dropdown:
            await self.with_dropdown(interaction)
        else:
            await self.without_dropdown(interaction)
