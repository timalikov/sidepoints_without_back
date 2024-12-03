from typing import Literal
import discord

from translate import translations
from bot_instance import get_bot

from services.logger.client import CustomLogger
from services.cache.client import custom_cache

logger = CustomLogger
bot = get_bot()


async def send_invitation(discord_user: discord.User, invite_link: str, channel_name: str, guild_id: int, lang: Literal["en", "ru"] = "en"):
    try:
        await discord_user.send(
            translations["private_channel_created"][lang].format(invite_link=invite_link)
        )

        custom_cache.set_user_invite(
            user_id=discord_user.id,
            invite_link=invite_link,
            channel_name=channel_name,
            guild_id=guild_id
        )

    except discord.Forbidden:
        await logger.error_discord(f"Error: Unable to send a DM to {discord_user.name}. They may have DMs disabled or the bot lacks permissions.")
    except discord.HTTPException as http_error:
        await logger.error_discord(f"HTTPException: Failed to send an invitation to {discord_user.name}. Error: {http_error}")
    except Exception as e:
        await logger.error_discord(f"An unexpected error occurred while sending an invitation to {discord_user.name}: {e}")
