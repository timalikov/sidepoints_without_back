import discord
from discord import app_commands
from discord.ext import commands

from bot_instance import get_bot
from database.dto.psql_services import Services_Database
from translate import get_lang_prefix, translations
from services.messages.interaction import send_interaction_message
from config import LINK_LEADERBOARD
from services.utils import save_user_id

bot = get_bot()


class LeaderboardCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Check out the points leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        guild_id: int = interaction.guild_id if interaction.guild_id else None
        await Services_Database().log_to_database(
        interaction.user.id, 
            "/leaderboard", 
            guild_id
            )
        await save_user_id(interaction.user.id)
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
            return
        await interaction.response.send_message(
            embed=discord.Embed(
                color=discord.Colour.orange(),
                title=translations["leaderboard_title"][lang],
                description=translations["leaderboard"][lang],
                url=LINK_LEADERBOARD
            ),
            ephemeral=True
        )