from typing import List

import asyncio
from commands.points_command import PointsCommand
import discord
import discord.ext
import discord.ext.commands
from logging import getLogger

from bot_instance import get_bot

from config import (
    MAIN_GUILD_ID,
    DISCORD_BOT_TOKEN,
    TEST,
)

main_guild_id: int = MAIN_GUILD_ID

bot = get_bot()
logger = getLogger("")



@bot.event
async def on_ready():
    production_commands: List[discord.ext.commands.Cog] = [
        PointsCommand,
    ]
    await asyncio.gather(*(bot.add_cog(cog(bot)) for cog in production_commands))
    await bot.tree.sync()
    
    print(f"We have logged in as {bot.user}. Is test: {'Yes' if TEST else 'No'}. Bot: {bot}")


# def run():
#     bot.run(DISCORD_BOT_TOKEN)
async def run_async():
    async with bot:
        await bot.start(DISCORD_BOT_TOKEN)

def run():
    asyncio.run(run_async())