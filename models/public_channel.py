import discord


async def find_channel_by_category_and_name(
    category_name: str,
    channel_name: str,
    guild: discord.Guild,
) -> discord.ChannelType:
    """Finds a channel by its category and name."""

    current_category: discord.CategoryChannel = None
    for category in guild.categories:
        if category.name.lower() == category_name.lower():
            current_category = category
            break
    
    for channel in current_category.channels:
        if channel.name.lower() == channel_name.lower():
            return channel

