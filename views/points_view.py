import os
from typing import Literal
from config import INVITE_BOT_URL, LEADERBOARD_IMAGE_URL, LINK_LEADERBOARD, MAIN_GUILD_ID
import discord
from services.cogs.invite_tracker import InviteTracker
from bot_instance import get_bot

bot = get_bot()

class PointsView(discord.ui.View):

    def __init__(
        self, 
        *,
        current_point: int,
        total_points: int,
        rank: int,
        lang: Literal["en", "ru"] = "en",
    ):
        super().__init__(timeout=None)
        self.current_point = current_point
        self.total_points = total_points
        self.rank = rank
        self.lang = lang

        self.embed_message = self._build_embed_message_points()
        self.add_item(discord.ui.Button(
            label="Add SideKick to your server",
            url=INVITE_BOT_URL,
            style=discord.ButtonStyle.link
        ))

    def _build_embed_message_points(self):
        embed = discord.Embed(
            title="Points",
            color=discord.Color.from_rgb(255,211,14)
        )
        embed.add_field(
            name="Total points",
            value=self.total_points,
            inline=True
        )
        embed.add_field(
            name="Leaderboard ranking",
            value=self.rank,
            inline=True
        )
        embed.add_field(
            name="Check out details here",
            value=f"{LINK_LEADERBOARD}?side_auth=DISCORD",
            inline=False
        )
        embed.set_image(url=LEADERBOARD_IMAGE_URL)
        return embed
    
    @discord.ui.button(label="Invite user to the SideKick Server", style=discord.ButtonStyle.primary)
    async def invite_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        max_age: int = 86400
        """
        Command to create an invite link using the InviteTracker cog's method.
        """
        invite_tracker: InviteTracker = bot.get_cog('InviteTracker')

        guild = bot.get_guild(MAIN_GUILD_ID)  

        if invite_tracker and guild:
            invite = await guild.system_channel.create_invite(max_age=max_age)  
            
            guild_id = guild.id
            if guild_id not in invite_tracker.invites:
                invite_tracker.invites[guild_id] = await guild.invites() 

            invite_tracker.invites[guild_id].append(invite)
            
            message = f"Invite link created: `{invite.url}`"
            await interaction.response.send_message(message, ephemeral=False)
        else:
            print("InviteTracker cog not loaded or Guild not found")
            message = "Something went wrong. Please try again later."
            await interaction.response.send_message(message, ephemeral=False)
