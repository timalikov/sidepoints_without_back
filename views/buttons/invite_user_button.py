import random
import string
from typing import Literal, Dict

import discord

from bot_instance import get_bot

from config import MAIN_GUILD_ID

from views.buttons.base_button import BaseButton
from services.logger.client import CustomLogger

logger = CustomLogger
bot = get_bot()


class InviteUserButton(BaseButton):
    def __init__(
        self,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Invite Friends",
            style=discord.ButtonStyle.primary,
            custom_id="invite_user",
            row=row
        )
        self.lang = lang
        self._view_variables = []
    
    async def callback(self, interaction: discord.Interaction):
        invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        embed_message = discord.Embed(
            title="Invite Link",
            description=(
                f"Your invite link has been created: https://discord.gg/{invite_code}\n\n"
                "Please share it with your friends. When they join the SideKicker server, you will earn **100 points**!"
            ),
            color=discord.Color.blue()
        )
            
        await interaction.response.send_message(embed=embed_message, ephemeral=True)