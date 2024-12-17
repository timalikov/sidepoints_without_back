from typing import Literal, Dict

import discord

from bot_instance import get_bot
from translate import translations

from models.payment import (
    create_wallet,
    is_wallet_exist_by_discord_id
)
from services.common_http import handle_status_code
from services.messages.interaction import send_interaction_message
from views.buttons.base_button import BaseButton

bot = get_bot()


class CreateWalletButton(BaseButton):
    def __init__(
        self,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Claim",
            style=discord.ButtonStyle.secondary,
            custom_id="create_wallet",
            row=row,
        )
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        is_exists = await is_wallet_exist_by_discord_id(interaction.user.id)
        is_success: bool = True
        if not is_exists:
            response = await create_wallet(interaction.user.id)
            is_success = await handle_status_code(response=response)
        embed = (
            discord.Embed(
                color=discord.Color.green(),
                description=translations["coupon_received_message"][self.lang]
            )
            if is_success else
            discord.Embed(
                description=translations["server_error_payment"][self.lang],
                colour=discord.Colour.red()
            )
        )
        await send_interaction_message(interaction=interaction, embed=embed)
