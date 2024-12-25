import random
import discord
from discord.ext import commands
from discord import app_commands

from bot_instance import get_bot
from translate import get_lang_prefix
from views.points_view import PointsView

bot = get_bot()


class PointsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="points", description="See your points and tasks")
    async def points(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        
        guild_id = interaction.guild_id if interaction.guild_id else None
        lang = get_lang_prefix(guild_id)
        username = interaction.user.name
        
        user_ranking = {
            "total_score": random.randint(0, 1000),
            "total_pos": random.randint(1, 100)
        }

        total_points = user_ranking.get('total_score', 0)
        rank = user_ranking.get('total_pos', 0)
        
        view = PointsView(
            username=username,
            user=interaction.user,
            total_points=total_points, 
            rank=rank, 
            lang=lang
        )
        send_method = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
        view.message = await send_method(embed=view.embed_message, view=view)
