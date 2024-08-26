import discord
from discord import ForumTag

from sql_forum_server import ForumsOfServerDatabase
from database.psql_services import Services_Database
from config import FORUM_NAME


async def create_base_forum(guild: discord.Guild) -> discord.ForumChannel:
    base_category_name = "SIDEKICK BOT"
    category = None
    index = 1
    while not category:
        category_name = f"{base_category_name}"
        category = discord.utils.get(guild.categories, name=category_name)
        if category and len(category.channels) >= 50:
            category = None
            index += 1
        elif not category:
            category = await guild.create_category(category_name)

    services_db = Services_Database()
    values_list = await services_db.get_all_active_tags()
    available_tags = [ForumTag(name=tag) for tag in values_list]
    new_forum_channel = await guild.create_forum(
        name=FORUM_NAME,
        topic="SideKickers Cards",
        category=category,
        available_tags=available_tags,
        overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)}
    )
    await ForumsOfServerDatabase.add_forum(str(guild.id), str(new_forum_channel.id))
    return new_forum_channel