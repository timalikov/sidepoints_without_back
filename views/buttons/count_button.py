from typing import Literal

import discord

from bot_instance import get_bot

from views.buttons.base_button import BaseButton

bot = get_bot()


class CountButton(BaseButton):
    def __init__(self,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ) -> None:
        super().__init__(label="0", style=discord.ButtonStyle.gray, row=row, disabled=True)
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
    