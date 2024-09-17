import discord

from models.category import (
    get_or_create_category_by_name,
    get_category_by_name
)


async def find_channel_by_category_and_name(
    category_name: str,
    channel_name: str,
    guild: discord.Guild,
) -> discord.ChannelType:
    """Finds a channel by its category and name."""

    current_category: discord.CategoryChannel = await get_category_by_name(
        guild=guild, category_name=category_name
    )
    if not current_category:
        return None
    return discord.utils.get(current_category.channels, name=channel_name)


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
    return channel
