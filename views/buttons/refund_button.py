from typing import Literal, Dict

import discord

from bot_instance import get_bot
from translate import translations

from database.dto.psql_services import Services_Database
from views.buttons.base_button import BaseButton
from services.refund_handler import RefundHandler
from services.messages.interaction import send_interaction_message

bot = get_bot()


class RefundButton(BaseButton):
    def __init__(
        self,
        *,
        refund_handler: RefundHandler,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Refund",
            style=discord.ButtonStyle.red,
            custom_id="refund_button",
            row=row,
            emoji="❌"
        )
        self.refund_handler
        self.lang = lang
        self._view_variables = ["channel", "disable_all_buttons"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "refund", 
            interaction.guild.id if interaction.guild else None
        )

        await send_interaction_message(
            interaction=interaction,
            message=translations['refund_requested'][self.lang]
        )

        await self.view.disable_all_buttons()

        await self.refund_handler.process_refund(
            interaction=None,
            success_message=translations['refund_success_customer'][self.lang],
            kicker_message=translations['refund_requested'][self.lang],
            customer_message=translations['refund_success_customer'][self.lang],
            channel=self.view.channel
        )
