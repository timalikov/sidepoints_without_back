import discord

from models.category import (
    get_or_create_category_by_name,
    get_category_by_name
)
from services.logger.client import CustomLogger
from database.dto.psql_guild_channels import DiscordGuildChannelsDTO
from config import (
    ORDER_CATEGORY_NAME,
    ORDER_CHANNEL_NAME,
    ANNOUNCEMENTS_CATEGORY_NAME,
    ANNOUNCEMENTS_CHANNEL_NAME,
    LEADERBOARD_CATEGORY_NAME,
    LEADERBOARD_CHANNEL_NAME,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME,
    WEB3_CHATTING_CHANNEL_NAME
)

logger = CustomLogger


async def _get_or_delete_channel_by_id(
    guild: discord.Guild,
    channel_id: int
) -> discord.ChannelType:
    dto = DiscordGuildChannelsDTO()
    channel_from_database = guild.get_channel(channel_id)
    if not channel_from_database:
        await dto.delete(channel_id)
    return channel_from_database


async def _get_channel_from_db(
    channel_name: str,
    guild: discord.Guild,
) -> discord.ChannelType:
    dto = DiscordGuildChannelsDTO()
    channel_id_from_db: int = await dto.get_channel_id_by_name(
        guild_id=guild.id, channel_name=channel_name
    )
    channel: discord.ChannelType = None
    if channel_id_from_db:
        channel = await _get_or_delete_channel_by_id(
            guild=guild, channel_id=channel_id_from_db
        )
    return channel


async def _get_channel_from_discord(
    category_name: str,
    channel_name: str,
    guild: discord.Guild,
) -> discord.ChannelType:
    current_category: discord.CategoryChannel = await get_category_by_name(
        guild=guild, category_name=category_name
    )
    if not current_category:
        return None
    channel: discord.TextChannel = discord.utils.get(
        current_category.channels,
        name=channel_name
    )
    return channel


async def find_channel_by_category_and_name(
    category_name: str,
    channel_name: str,
    guild: discord.Guild,
) -> discord.ChannelType:
    """Finds a channel by its category and name."""

    channel_from_db = await _get_channel_from_db(
        guild=guild,
        channel_name=channel_name
    )
    if channel_from_db:
        return channel_from_db
    channel_from_discord = await _get_channel_from_discord(
        guild=guild,
        channel_name=channel_name,
        category_name=category_name
    )
    if channel_from_discord and not channel_from_db:
        dto = DiscordGuildChannelsDTO()
        await dto.create(guild.id, channel_name, channel_from_discord.id)
    return channel_from_discord


async def get_or_create_channel_by_category_and_name(
    category_name: str,
    channel_name: str,
    guild: discord.Guild,   
) -> discord.TextChannel:
    channel = await find_channel_by_category_and_name(
        category_name=category_name,
        channel_name=channel_name,
        guild=guild,
    )
    if not channel:
        category = await get_or_create_category_by_name(
            guild=guild, category_name=category_name
        )
        channel = await guild.create_text_channel(name=channel_name, category=category)
        dto = DiscordGuildChannelsDTO()
        await dto.create(guild.id, channel_name, channel.id)
    return channel


async def create_all_required_channels(guild: discord.Guild) -> None:
    channels = [
        (GUIDE_CATEGORY_NAME, GUIDE_CHANNEL_NAME),
        (ANNOUNCEMENTS_CATEGORY_NAME, ANNOUNCEMENTS_CHANNEL_NAME),
        (ORDER_CATEGORY_NAME, ORDER_CHANNEL_NAME),
        (ORDER_CATEGORY_NAME, WEB3_CHATTING_CHANNEL_NAME),
        (LEADERBOARD_CATEGORY_NAME, LEADERBOARD_CHANNEL_NAME),
    ]
    for category_name, channel_name in channels:
        _ = await get_or_create_channel_by_category_and_name(
            category_name=category_name,
            channel_name=channel_name,
            guild=guild
        )
    await logger.error_discord(f"Channels created in {guild.name}")
