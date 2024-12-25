from typing import Literal

from datetime import datetime
import discord

from bot_instance import get_bot
from config import MAIN_GUILD_ID, TEST_ACCOUNTS
from services.messages.invite_to_private_channel import send_invitation
from translate import get_lang_prefix, translations

from message_tasks import start_all_messages
from database.dto.sql_profile import Profile_Database
from services.schedule_tasks.session_delivery_check import session_delivery_check
from services.logger.client import CustomLogger
from services.messages.customer_support_messenger import send_message_to_customer_support, send_message_to_team_channel
from views.buttons.done_button import DoneButton

main_guild_id = MAIN_GUILD_ID
bot = get_bot()
logger = CustomLogger


async def send_connect_message_between_kicker_and_customer(
    challenger: discord.User,
    challenged: discord.User,
    serviceName: str,
    invite_url: str = None,
    lang: Literal["en", "ru"] = "en",
) -> None:
    kicker_message = translations["kicker_session_started_message"][lang].format(
        challenger_id=challenger.id,
        challenger_name=challenger.name,
        service_name=serviceName
    )
    kicker_embed = discord.Embed(
        title=translations["kicker_session_started_message_title"][lang],
        description=kicker_message,
        colour=discord.Colour.green()
    )
    user_message_embed = discord.Embed(
        title=translations["order_confirmed"][lang],
        description=translations["user_order_accepted_message"][lang].format(
            challenged_id=challenged.id,
            challenged_name=challenged.name,
            service_name=serviceName
        ),
        color=discord.Color.red()
    )
    
    if invite_url:
        kicker_embed.add_field(
            name="Invite link",
            value=invite_url
        )
        user_message_embed.add_field(
            name="Invite link",
            value=invite_url
        )

    try:
        await challenger.send(embed=user_message_embed)
        if challenged.id != 1208433940050874429:
            await challenged.send(embed=kicker_embed)
    except discord.HTTPException:
        await logger.error_discord("Failed to send invite links to one or more participants.")

async def manage_connection_messages(
    guild, challenger, challenged, serviceName, invite_url, channel_name, guild_id, lang
):
    challenged_in_guild = guild.get_member(challenged.id) is not None
    
    if challenged_in_guild:
        await send_connect_message_between_kicker_and_customer(
            challenger=challenger,
            challenged=challenged,
            serviceName=serviceName,
            invite_url=invite_url,
            lang=lang
        )
    else:
        await send_invitation(
            discord_user=challenged,
            invite_link=invite_url,
            channel_name=channel_name,
            guild_id=guild_id,
            lang=lang
        )
        
        user_message_embed = discord.Embed(
            title=translations["order_confirmed"][lang],
            description=translations["user_order_accepted_message"][lang].format(
                challenged_id=challenged.id,
                challenged_name=challenged.name,
                service_name=serviceName
            ),
            color=discord.Color.red()
        )
        user_message_embed.add_field(
            name="Invite link",
            value=invite_url
        )
        await challenger.send(embed=user_message_embed)
        
async def create_private_discord_channel(
    bot_instance,
    guild_id,
    challenger,
    challenged,
    serviceName,
    kicker_username,
    purchase_id,
    base_category_name="Sidekick Chatrooms",
    lang: Literal["en", "ru"] = "en",
):
    guild = bot.get_guild(guild_id)

    category = None
    index = 1
    while not category:
        category_name = f"{base_category_name}{index}"
        category = discord.utils.get(guild.categories, name=category_name)
        if category and len(category.channels) >= 50:
            category = None
            index += 1
        elif not category:
            category = await guild.create_category(category_name)

    kicker_role: discord.Role = discord.utils.get(guild.roles, name="Kicker")  
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        kicker_role: discord.PermissionOverwrite(read_messages=True),
        challenger: discord.PermissionOverwrite(read_messages=True),
        challenged: discord.PermissionOverwrite(read_messages=True),
    }

    formatted_time = datetime.now().strftime("%H:%M_%d.%m.%y")    
    channel_name = f"{challenged.name}_{challenger.name}_{formatted_time}"

    channel = await category.create_voice_channel(channel_name, overwrites=overwrites)

    invite = await channel.create_invite(max_age=86400, max_uses=10)

    welcome_message = translations["welcome_message"][lang].format(kicker_username=kicker_username)
    await channel.send(welcome_message)
    
    await start_all_messages(channel)

    manager_message = translations["session_started_message"][lang].format(
        challenged=challenged,
        challenger=challenger,
        invite_url=invite.url
    )

    await manage_connection_messages(
        guild=guild,
        challenger=challenger,
        challenged=challenged,
        serviceName=serviceName,
        invite_url=invite.url,
        channel_name=channel_name,
        guild_id=guild_id,
        lang=lang,
    )

    if challenged.id not in TEST_ACCOUNTS and challenger.id not in TEST_ACCOUNTS:
        await send_message_to_customer_support(bot, manager_message)
        await send_message_to_team_channel(bot=bot, customer=challenger, kicker=challenged, invite_url=invite.url)

    await session_delivery_check(
        customer=challenger,
        kicker=challenged,
        purchase_id=purchase_id,
        channel=channel,
        lang=lang
    )
    if challenged.id == 1208433940050874429:
        # Creating the embed
        embed = discord.Embed(
            title="👋 Hi there! Welcome to the Web3 Mastery Tutorial!", 
            description=translations["kicker_intro_message"][lang], 
            color=discord.Color.blue()
        )
        view = discord.ui.View(timeout=None)
        view.add_item(DoneButton(lang=lang))
        await channel.send(embed=embed, view=view)
    return True, channel

async def send_challenge_invites(
    challenger: discord.User,
    challenged: discord.User, 
    invite_url: str,
    lang: Literal["en", "ru"] = "en",
):
    invite_message = translations["challenge_invite_message"][lang].format(invite_url=invite_url)
    await challenger.send(invite_message)
    if challenged.id != challenger.id:
        await challenged.send(invite_message)


async def join_or_create_private_discord_channel(
    bot,
    guild_id: int,
    challenge,
    challenger: discord.User,
    challenged: discord.User
):
    guild = bot.get_guild(guild_id)
    lang = get_lang_prefix(guild_id)
    existing_channel_ids = await Profile_Database.get_channel_id_by_user_id(challenged.id)
    channel = None

    # Check if any of the fetched channel IDs exist in the guild
    for channel_id in existing_channel_ids:
        channel = guild.get_channel(channel_id)
        if channel:
            break

    channel_name = f"team-{challenged.display_name}"
    # If no valid channel is found, create a new one
    if not channel:
        success, channel = await create_private_discord_channel(
            bot,
            guild_id,
            challenge,
            channel_name,
            challenger,
            challenged,
            base_category_name="Sidekick Team Rooms",
            lang=lang
        )
        if not success:
            return False, "Failed to create a new private channel"
        await Profile_Database.add_channel_to_user(challenged.id, channel.id)

    await channel.set_permissions(challenger, read_messages=True)
    await channel.set_permissions(challenged, read_messages=True)

    try:
        invite = await channel.create_invite(max_age=14400)  # Create a 4-hour invite
        await send_challenge_invites(challenger, challenged, invite.url, lang=lang)
        return True, channel
    except discord.HTTPException:
        return False, "Failed to send invite links to one or more participants."

async def create_private_channel_for_user_and_role(
    guild: discord.Guild,
    user: discord.User,
    role_name: str,
    category_name: str
) -> tuple[bool, discord.abc.GuildChannel | None]:
    """
    Creates a private channel for a specific user and role within a guild.
    """
    try:
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found.")
        
        index = 1
        while True:
            current_category_name = category_name if index == 1 else f"{category_name}_{index}"
            category = discord.utils.get(guild.categories, name=current_category_name)
            if not category:
                category = await guild.create_category(current_category_name)
            if category and len(category.channels) < 50:
                break
            index += 1
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
            user: discord.PermissionOverwrite(read_messages=True)
        }

        formatted_time = datetime.now().strftime("%H:%M_%d.%m.%y")
        channel_name = f"{role_name}-{user.name}-{formatted_time}"
        channel = await category.create_voice_channel(channel_name, overwrites=overwrites)
        return True, channel
    except (discord.DiscordException, ValueError) as e:
        logger.error(f"Error creating private channel for {category_name}, {role_name}: {e}")
        return False, None