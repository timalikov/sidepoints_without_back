from typing import List

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
    permissions = discord.PermissionOverwrite(
        create_instant_invite=True,
        kick_members=False,
        ban_members=False,
        administrator=False,
        manage_channels=False,
        manage_guild=False,
        add_reactions=False,
        view_audit_log=False,
        priority_speaker=False,
        stream=False,
        read_messages=True,
        view_channel=True,
        send_messages=False,
        send_tts_messages=False,
        manage_messages=False,
        embed_links=False,
        attach_files=False,
        read_message_history=False,
        mention_everyone=False,
        view_guild_insights=False,
        connect=False,
        speak=False,
        mute_members=False,
        deafen_members=False,
        move_members=False,
        use_voice_activation=False,
        change_nickname=False,
        manage_nicknames=False,
        manage_roles=False,
        manage_permissions=False,
        manage_webhooks=False,
        manage_expressions=False,
        manage_emojis=False,
        manage_emojis_and_stickers=False,
        use_application_commands=False,
        request_to_speak=False,
        manage_events=False,
        manage_threads=False,
        create_public_threads=False,
        create_private_threads=False,
        send_messages_in_threads=False,
        external_stickers=False,
        use_external_stickers=False,
        use_embedded_activities=False,
        moderate_members=False,
        use_soundboard=False,
        use_external_sounds=False,
        send_voice_messages=False,
        create_expressions=False,
    )
    new_forum_channel = await guild.create_forum(
        name=FORUM_NAME,
        topic="SideKickers Cards",
        category=category,
        available_tags=available_tags,
        overwrites={guild.default_role: permissions},
        default_layout=discord.ForumLayoutType.gallery_view
    )
    await ForumsOfServerDatabase.add_forum(str(guild.id), str(new_forum_channel.id))
    return new_forum_channel


async def find_thread_in_forum_by_ids(
    forum: discord.ForumChannel,
    thread_ids: List[int]
) -> List[discord.Thread]:
    return [forum.get_thread(thread_id) for thread_id in thread_ids]