from typing import Literal, Dict

import discord

from bot_instance import get_bot
from translate import translations

from database.dto.psql_services import Services_Database
from views.buttons.base_button import BaseButton

bot = get_bot()


class RejectButton(BaseButton):
    def __init__(
        self,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Reject",
            style=discord.ButtonStyle.secondary,
            custom_id="reject",
            row=row,
            emoji="❌"
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        try:
            await self.view.stop_refund_manager()
            await self.view.refund_manager.send_refund_replace(start_timer=True)
        except (AttributeError, Exception):
            await self.view.disable_all_buttons()
        finally:
            await Services_Database().log_to_database(
                interaction.user.id, 
                "user_reject_after_order", 
                interaction.guild.id if interaction.guild else None
            )
            try:
                self.view.already_pressed = True
            except AttributeError:
                pass
            await interaction.message.edit(embed=discord.Embed(description=translations['canceled'][self.lang]), view=None)
