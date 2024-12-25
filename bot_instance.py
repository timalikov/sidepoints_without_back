from discord.ext import commands
import discord

# Setup intents
intents = discord.Intents.default()

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)
def get_bot():
    return bot
