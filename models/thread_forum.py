from typing import Union, Literal
import asyncio

import discord

from models.post_forum import Post_FORUM

from database.dto.sql_forum_posted import ForumUserPostDatabase 
from database.dto.psql_services import Services_Database


async def find_thread_in_forum(
    guild: discord.Guild,
    forum: discord.ForumChannel,
    profile_data: dict
) -> Union[discord.Thread, bool]:
    existing_thread_ids = await ForumUserPostDatabase.get_thread_id_by_user_and_forum_multi(
        user_id=profile_data['discord_id'], forum_id=forum.id
    )
    thread: Union[bool, discord.Thread] = False
    if existing_thread_ids:
        for existing_thread_id in existing_thread_ids:
            try:
                thread = await guild.fetch_channel(int(existing_thread_id))
            except discord.errors.DiscordException:
                continue
            if [profile_data["service_type_name"]] == [i.name for i in thread.applied_tags]:
                break
            thread = False
    return thread


async def start_posting(
    forum_channel: discord.ForumChannel,
    guild: discord.Guild,
    bot,
    order_type: Literal["DESC", "ASC"] = "DESC"
) -> None:
    dto = Services_Database(order_type=order_type)
    services = await dto.get_all_services()
    guild_members: list[dict] = []
    not_guild_members: list[dict] = []
    for service in services:
        if guild.get_member(
            int(service["discord_id"])
        ):
            guild_members.append(service)
        else:
            not_guild_members.append(service)
    services = not_guild_members + guild_members
    for profile_data in services:
        thread: Union[bool, discord.Thread] = await find_thread_in_forum(
            guild=guild, forum=forum_channel, profile_data=profile_data
        )
        if thread and thread.archived:
            await thread.edit(archived=False)
        temp_post = Post_FORUM(bot, profile_data, forum_channel, thread)
        await temp_post.post_user_profile()
        await asyncio.sleep(1)