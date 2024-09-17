import discord


async def get_category_by_name(
    *,
    guild: discord.Guild,
    category_name: str
) -> discord.CategoryChannel:
    return discord.utils.get(guild.categories, name=category_name)


async def get_or_create_category_by_name(
    *,
    guild: discord.Guild,
    category_name: str
) -> discord.CategoryChannel:
    category = await get_category_by_name(guild=guild, category_name=category_name)
    if not category:
        category = await guild.create_category(category_name)
    return category
