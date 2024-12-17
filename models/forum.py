from typing import Optional

import discord
from discord import ForumTag

from bot_instance import get_bot
from config import FORUM_NAME, FORUM_CATEGORY_NAME, SERVER_TYPE

from database.dto.sql_forum_posted import ForumUserPostDatabase
from database.dto.psql_services import Services_Database
from database.dto.psql_guild_channels import DiscordGuildChannelsDTO
from models.category import get_or_create_category_by_name
from models.public_channel import (
    _get_channel_from_db,
    _get_or_delete_channel_by_id,
)

bot = get_bot()


async def find_forum(
    guild: discord.Guild,
    forum_name: str
) -> Optional[discord.ForumChannel]:
    forum_channel = await _get_channel_from_db(
        guild=guild,
        channel_name=forum_name
    )
    if forum_channel:
        return forum_channel
    dto = DiscordGuildChannelsDTO()
    for channel in guild.channels:
        if channel.name == forum_name and isinstance(channel, discord.channel.ForumChannel):
            forum_channel = channel
            await dto.create(guild.id, forum_channel.name, forum_channel.id)
    return forum_channel


async def find_sidekick_forum(guild: discord.Guild) -> Optional[discord.ForumChannel]:
    return await find_forum(guild=guild, forum_name=FORUM_NAME)


async def create_base_forum(guild: discord.Guild) -> discord.ForumChannel:
    category = await get_or_create_category_by_name(guild=guild, category_name=FORUM_CATEGORY_NAME)
    services_db = Services_Database()
    tags = await services_db.get_all_active_tags()
    values_list = ["Male", "Female"] + list(tags) 
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
    dto = DiscordGuildChannelsDTO()
    await dto.create(guild.id, FORUM_NAME, new_forum_channel.id)
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
        _ = [await thread.delete() for thread in forum_channel.threads]
        await dto.delete_by_forum_id(forum_channel.id)
        services_db = Services_Database()
        tags = await services_db.get_all_active_tags()
        values_list = ["Male", "Female"] + list(tags)
        await forum_channel.edit(available_tags=[])
        available_tags = [
            ForumTag(name=tag)
            for tag in values_list[:20]
        ]
        await forum_channel.edit(available_tags=available_tags)
        return forum_channel
    forum_channel = await create_base_forum(guild)
    return forum_channel


def get_tag_emoji(tag_name: str) -> discord.Emoji:
    emojis = {
        "LOCAL": {
            "league of legends": ("lol", 1315594937269620786),
            "valorant": ("valorant", 1315594911268995113),
            "cs:go": ("csgo2", 1315594879186894919),
            "apex legends": ("apex", 1315594838447489105),
            "world of tanks": ("tankworld", 1315594806139027549),
            "dota 2": ("dota2", 1315594775151247381),
            "pubg": ("pubg", 1315594637582274560),
            "naraka": ("naraka", 1315594593013862411),
            "overwatch 2": ("overwatch2", 1315594549225197598),
            "fortnite": ("fortnite", 1315594507143614494),
            "teamfight tactics": ("tft", 1315594477091553311),
            "steam": ("steam", 1315594425325457418),
            "youtube": ("youtube", 1315594398939222028),
            "gta 5": ("gta5", 1315594377896263751),
            "arena": ("arena", 1315594357906210828),
            "just chatting": ("chatting", 1315594334443147274),
            "virtual dating": ("virturdate", 1315594301161345075),
            "male": ("male", 1315594246337859625),
            "female": ("female", 1315594210241413120)
        },
        "TEST": {},
        "PRODUCTION": {}
    }
    emoji = emojis[SERVER_TYPE].get(tag_name.lower())
    emoji_format = "<:{emoji_name}:{emoji_id}>"
    return emoji_format.format(
        emoji_name=emoji[0],
        emoji_id=emoji[1]
    ) if emoji else None
