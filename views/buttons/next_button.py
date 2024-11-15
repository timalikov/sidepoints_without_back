from typing import Literal

import discord

from bot_instance import get_bot
from translate import translations

from services.kicker_sort_service import KickerSortingService
from database.dto.psql_services import Services_Database
from views.buttons.base_button import BaseButton

bot = get_bot()


class NextButton(BaseButton):
    def __init__(
        self,
        *,
        kicker_sorting_service: KickerSortingService = None,
        row: int | None = None,
        is_list: bool = False,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="next", row=row)
        self.kicker_sorting_service = kicker_sorting_service
        self.is_list = is_list
        self.lang = lang
        self._view_variables = [
            ("service", "set_service", "profile_embed"),  # KickerSortingService
            ("service", "user_id", "profile_embed", "service_index", "services", "service_db")  # List
        ]

    async def next_list_object(self, interaction: discord.Interaction) -> None:
        await self.view.set_service()
        await interaction.edit_original_response(embed=self.view.profile_embed, view=self.view)

    async def next_database_object(self, interaction: discord.Interaction) -> None:
        next_service = await self.kicker_sorting_service.get_next_valid_service()
        if next_service:
            self.view.set_service(next_service)
            await interaction.edit_original_response(embed=self.view.profile_embed, view=self.view)
        else:
            await interaction.followup.send(
                translations["no_valid_players"][self.lang],
                ephemeral=True
            )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "next_kicker", 
            interaction.guild.id if interaction.guild else None
        )
        if self.is_list:
            await self.next_list_object(interaction)
        else:
            await self.next_database_object(interaction)
