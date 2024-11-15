import discord
from discord.ext import commands
from discord import app_commands

from bot_instance import get_bot
from translate import get_lang_prefix
from database.dto.psql_services import Services_Database
from database.dto.psql_leaderboard import LeaderboardDatabase
from models.payment import get_server_wallet_by_discord_id
from views.points_view import PointsView
from services.utils import save_user_id

bot = get_bot()


class PointsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="points", description="See your points and tasks")
    async def points(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        
        user_id = interaction.user.id
        services_db = Services_Database()
        await services_db.log_to_database(
            user_id, 
            "/points", 
            interaction.guild.id if interaction.guild else None
        )
        await save_user_id(user_id)
        guild_id = interaction.guild_id if interaction.guild_id else None
        lang = get_lang_prefix(guild_id)
        username = interaction.user.name
        profile_id = await services_db.get_user_profile_id(discord_id=user_id)
        if not profile_id:
            await get_server_wallet_by_discord_id(user_id)
            user_ranking = {"total_score": 0, "total_pos": 0}
        else:
            dto = LeaderboardDatabase()
            user_ranking = await dto.get_user_ranking(profile_id=profile_id)
            
            total_points = user_ranking.get('total_score', 0) if user_ranking else 0
            rank = user_ranking.get('total_pos', 0) if user_ranking else 0
            view = PointsView(
                username=username,
                user=interaction.user,
                total_points=total_points, 
                rank=rank, 
                lang=lang
            )
        send_method = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
        await send_method(embed=view.embed_message, view=view)
