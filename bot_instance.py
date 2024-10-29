from discord.ext import commands
import discord

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.guilds = True
intents.moderation = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)
def get_bot():
    return bot
