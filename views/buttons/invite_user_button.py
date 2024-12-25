from typing import Literal, Dict

import discord

from bot_instance import get_bot

from config import MAIN_GUILD_ID

from services.cogs.invite_tracker import InviteTracker
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
        max_age: int = 86400
        
        invite_tracker: InviteTracker = bot.get_cog('InviteTracker')
        guild = bot.get_guild(MAIN_GUILD_ID)  

        if invite_tracker and guild:
            channel = guild.text_channels[0]  
            guild_id = guild.id

            invite_tracker.invites[guild_id] = await guild.invites() 
            invite = await channel.create_invite(max_age=max_age, unique=True)
            invite_tracker.manual_invites[invite.code] = interaction.user
            
            embed_message = discord.Embed(
                title="Invite Link",
                description=(
                    f"Your invite link has been created: https://discord.gg/{invite.code}\n\n"
                    "Please share it with your friends. When they join the SideKicker server, you will earn **100 points**!"
                ),
                color=discord.Color.blue()
            )
            
            await interaction.response.send_message(embed=embed_message, ephemeral=True)
            
        else:
            logger.error("InviteTracker cog not loaded or Guild not found")
            error_message = discord.Embed(
                description="Something went wrong. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_message, ephemeral=True)
