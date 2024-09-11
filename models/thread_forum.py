from typing import Union

import discord

from database.dto.sql_forum_posted import ForumUserPostDatabase 


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