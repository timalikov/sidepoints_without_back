import discord
from discord import app_commands
from discord.ext import commands
from bot_instance import get_bot

from services.messages.interaction import send_interaction_message

bot = get_bot()


class TestCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="это тестовая команда для теста 2!")
    async def test(self, interaction: discord.Interaction):
        await send_interaction_message(interaction=interaction, message="<:lol:1315594937269620786>")