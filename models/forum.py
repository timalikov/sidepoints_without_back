from typing import Optional

import discord
from discord import ForumTag

from database.dto.sql_forum_server import ForumsOfServerDatabase
from database.dto.sql_forum_posted import ForumUserPostDatabase
from database.dto.psql_services import Services_Database
from config import FORUM_NAME, FORUM_CATEGORY_NAME
from models.category import get_or_create_category_by_name


async def find_forum(guild: discord.Guild, forum_name: str) -> Optional[discord.ForumChannel]:
    forum_channels = guild.channels
    forum_channel: discord.channel.ForumChannel = None
    for channel in forum_channels:
        if channel.name == forum_name and isinstance(channel, discord.channel.ForumChannel):
            forum_channel = channel
    return forum_channel


async def find_sidekick_forum(guild: discord.Guild) -> Optional[discord.ForumChannel]:
    return await find_forum(guild=guild, forum_name=FORUM_NAME)


async def create_base_forum(guild: discord.Guild) -> discord.ForumChannel:
    category = await get_or_create_category_by_name(guild=guild, category_name=FORUM_CATEGORY_NAME)
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
        view_audit_log=True,
        priority_speaker=False,
        stream=False,
        read_messages=True,
        view_channel=True,
        send_messages=False,
        send_tts_messages=False,
        manage_messages=False,
        embed_links=False,
        attach_files=False,
        read_message_history=True,
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


async def get_or_create_forum(guild: discord.Guild) -> discord.ForumChannel:
    forum_channel: discord.channel.ForumChannel = await find_sidekick_forum(guild)
    if not forum_channel:
        forum_channel = await create_base_forum(guild)
    return forum_channel


async def get_and_recreate_forum(guild: discord.Guild) -> discord.ForumChannel:
    forum_channel: discord.channel.ForumChannel = await find_sidekick_forum(guild)
    if forum_channel:
        dto = ForumUserPostDatabase()
        await forum_channel.delete()
        await dto.delete_by_forum_id(forum_channel.id)
    forum_channel = await create_base_forum(guild)
    return forum_channel
