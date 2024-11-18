import discord
from discord import app_commands
from discord.ext import commands
from bot_instance import get_bot
from config import TEST

bot = get_bot()


class TestCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="это тестовая команда для теста!")
    async def test(self, interaction: discord.Interaction):
        await interaction.user.send("test")