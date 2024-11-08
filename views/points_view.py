from typing import Literal
import discord

from config import (
    INVITE_BOT_URL,
    POINTS_IMAGE_URL,
    LINK_LEADERBOARD,
    MAIN_GUILD_ID,
    CHECK_IN_URL,
    YELLOW_LOGO_COLOR,
)
from views.check_in_button import CheckInButton
from services.cogs.invite_tracker import InviteTracker
from services.logger.client import CustomLogger
from bot_instance import get_bot
from translate import translations

logger = CustomLogger
bot = get_bot()

class PointsView(discord.ui.View):

    def __init__(
        self, 
        *,
        user: discord.User,
        username: str,
        total_points: int,
        rank: int,
        lang: Literal["en", "ru"] = "en",
    ):
        super().__init__(timeout=None)
        self.username = username
        self.total_points = total_points
        self.rank = rank
        self.lang = lang

        self.embed_message = self._build_embed_message_points()
        self.add_item(discord.ui.Button(
            label="Add Sidekick to your server",
            url=INVITE_BOT_URL,
            style=discord.ButtonStyle.link,
            row=1
            )
        )
        self.add_item(
            CheckInButton(user=user, total_points=total_points, lang=lang, row=3)
        )

    def _build_embed_message_points(self):
        embed = discord.Embed(
            title=self.username + " " + translations["points"][self.lang],
            color=discord.Color.from_rgb(*YELLOW_LOGO_COLOR)
        )
        embed.add_field(
            name=translations["total_points"][self.lang],
            value=self.total_points,
            inline=True
        )
        embed.add_field(
            name=translations["leaderboard_ranking"][self.lang],
            value=self.rank if self.rank != 0 else "-",
            inline=True
        )
        embed.add_field(
            name=translations["check_out_details"][self.lang],
            value=f"{LINK_LEADERBOARD}?side_auth=DISCORD",
            inline=False
        )
        embed.set_image(url=POINTS_IMAGE_URL)
        return embed
    
    @discord.ui.button(label="Invite user to the SideKick Server", style=discord.ButtonStyle.primary, row=0)
    async def invite_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        max_age: int = 86400
        
        invite_tracker: InviteTracker = bot.get_cog('InviteTracker')
        guild = bot.get_guild(MAIN_GUILD_ID)  

        if invite_tracker and guild:
            channel = guild.text_channels[0]  
            invite = await channel.create_invite(max_age=max_age, unique=True)
            
            guild_id = guild.id
            if guild_id not in invite_tracker.invites:
                invite_tracker.invites[guild_id] = await guild.invites() 

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
            print("InviteTracker cog not loaded or Guild not found")
            error_message = discord.Embed(
                description="Something went wrong. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_message, ephemeral=True)
