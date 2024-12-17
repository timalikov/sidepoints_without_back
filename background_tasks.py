import asyncio
import csv
from logging import getLogger

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Set
from database.dto.psql_roles import RolesDTO
import discord
from bot_instance import get_bot
from services.messages.base import send_to_channels
from translate import translations, get_lang_prefix
from discord.ext import tasks
from config import (
    MAIN_GUILD_ID,
    LEADERBOARD_CATEGORY_NAME,
    LEADERBOARD_CHANNEL_NAME,
    GUILDS_FOR_TASKS,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME,
    ORDER_CHANNEL_NAME,
)
from models.public_channel import get_or_create_channel_by_category_and_name
from models.forum import get_and_recreate_forum
from models.thread_forum import start_posting
from models.payment import get_server_wallet_by_discord_id
from services.cache.client import custom_cache
from services.logger.client import CustomLogger
from web3_interaction.balance_checker import get_usdt_balance
from database.dto.psql_leaderboard import LeaderboardDatabase
from database.dto.psql_services import Services_Database
from views.buttons.create_wallet_button import CreateWalletButton
from views.base_view import BaseView

main_guild_id = MAIN_GUILD_ID
bot = get_bot()
logger = CustomLogger


@tasks.loop(count=1)  # Ensure this runs only once
async def revoke_channel_access(channel, member):
    await asyncio.sleep(3600)  # Sleep for one hour (3600 seconds)
    await channel.set_permissions(member, overwrite=None)  # Remove specific permissions for this member


###########################################################################################################################
###########################################################################################################################
@tasks.loop(hours=6)  # Checks every 30 minutes
async def delete_old_channels():
    for guild in bot.guilds:  # Iterates over all guilds the bot is in
        # Retrieve all categories that match the naming pattern "Sidekick ChatroomsX"
        chatroom_categories = [cat for cat in guild.categories if cat.name.startswith("Sidekick Chatrooms")]
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)  # Current time in UTC with timezone aware

        # Iterate over each category in the guild
        for category in chatroom_categories:
            for channel in category.text_channels:
                time_diff = current_time - channel.created_at
                if time_diff > timedelta(hours=12):
                    await channel.delete(reason="Cleanup: Channel older than 24 hours.")


posted_user_ids_file = 'posted_user_ids.csv'

async def delete_all_threads_and_clear_csv():
    for i in [1248487428872994866]:
        forum_channel = bot.get_channel(i)
        if isinstance(forum_channel, discord.ForumChannel):
            for thread in forum_channel.threads:
                await thread.delete()
        else:
            pass

    # Clear the CSV file
    with open(posted_user_ids_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([])


guide_message_count: int = 0


@tasks.loop(hours=24)
async def assign_roles_to_kickers() -> None:
    guild: discord.Guild = bot.get_guild(int(MAIN_GUILD_ID))
    if not guild:
        logger.error("Guild not found. Check if the MAIN_GUILD_ID is correct.")
        return

    dto = Services_Database()
    
    try:
        super_kicker_ids: Set[int] = await dto.get_super_kickers()
    except Exception:
        await logger.error_discord("Failed to fetch super kickers from database.")
        raise

    for super_kicker_id in super_kicker_ids:
        member: Optional[discord.Member] = guild.get_member(super_kicker_id)
        if not member:
            continue

        try:
            services: List[Dict[str, str]] = await dto.get_services_by_discordId(super_kicker_id)
        except Exception as e:
            await logger.error_discord(f"Failed to fetch services for discord ID {super_kicker_id}.")
            continue
        
        if not services:
            logger.info(f"No services found for member {member.display_name} ({member.id}).")
            continue
        
        kicker_role = await get_or_create_role(guild, 'Kickers')
        await assign_role(member, kicker_role)
        for service in services:
            service_tag = service.get("tag")
            if service_tag:
                role = await get_or_create_role(guild, service_tag)
                await assign_role(member, role)
                await asyncio.sleep(1)

            service_lang = service.get("profile_languages") or []
            if not isinstance(service_lang, list):
                logger.warning(f"Expected list for 'profile_languages', got {type(service_lang).__name__}. Converting to list.")
                service_lang = [service_lang]

            for lang in service_lang:
                role = await get_or_create_role(guild, lang)
                await assign_role(member, role)
                await asyncio.sleep(1)

async def get_or_create_role(guild: discord.Guild, tag: str) -> Optional[discord.Role]:
    dto = RolesDTO()
    role_id: int = await dto.get_role_id_by_tag(tag, guild.id)
    if role_id:
        role: Optional[discord.Role] = discord.utils.get(guild.roles, id=role_id)
        if role:
            return role

    try:
        role = await guild.create_role(name=tag)
        await dto.save_role_id_by_tag(tag, guild.id, role.id)
        return role
    except discord.Forbidden:
        logger.error(f"Missing permissions to create role '{tag}' in guild '{guild.name}'.")
    except discord.HTTPException as e:
        await logger.error_discord(f"Failed to create role '{tag}' in guild '{guild.name}': {e}")
    return None

async def assign_role(member: discord.Member, role: Optional[discord.Role]) -> None:
    if not role:
        logger.warning(f"Role not found or could not be created for ")
        return

    if role in member.roles:
        return

    try:
        await member.add_roles(role)
    except discord.Forbidden:
        logger.error(f"Missing permissions to add role '{role.name}' to member {member.display_name} ({member.id}).")
    except discord.HTTPException as e:
        await logger.error_discord(f"Failed to add role '{role.name}' to member {member.display_name} ({member.id}): {e}")


@tasks.loop(hours=12)
async def send_random_guide_message() -> None:
    messages = [
        translations["guide_message_1"],
        translations["guide_message_2"],
        translations["guide_message_3"],
    ]
    global guide_message_count
    guide_message_count = (guide_message_count + 1) % 3
    for guild in bot.guilds:
        lang = get_lang_prefix(guild.id)
        message = messages[guide_message_count][lang]
        try:
            await send_to_channels(
                guild=guild,
                category_name=GUIDE_CATEGORY_NAME,
                channels=[ORDER_CHANNEL_NAME], 
                message=message,
                image_url="https://discord-photos.s3.eu-central-1.amazonaws.com/sidekick-back-media/discord_bot/%3AHow+to+make+an+order.png"
            )
        except discord.DiscordException as e:
            logger.error(str(e))


@tasks.loop(hours=24)
async def post_user_profiles():
    bot = get_bot()  # Assuming you have a function to get your bot instance
    tasks: List[asyncio.Task] = []
    for guild in bot.guilds:
        print("START LOOP POST", guild.name)
        try:
            forum_channel: discord.channel.ForumChannel = await get_and_recreate_forum(guild)
        except discord.DiscordException as e:
            await logger.error_discord(str(e))
            continue
        task = asyncio.create_task(
            start_posting(
                forum_channel=forum_channel, guild=guild, bot=bot, order_type="ASC"
            )
        )
        tasks.append(task)
    asyncio.gather(*tasks)


@tasks.loop(hours=24)
async def rename_kickers():
    guild = bot.get_guild(int(MAIN_GUILD_ID))
    if not guild:
        return
    dto = Services_Database()
    kickers = await dto.get_id_and_gender_kickers()
    names: Dict[str, str] = {
        "MALE": "『Kicker🎮{username}』",
        "FEMALE": "『Kicker🍧{username}』"
    }
    for kicker in kickers:
        try:
            _id = int(kicker["discord_id"])
        except (ValueError, TypeError):
            continue
        member = guild.get_member(_id)
        if not member:
            continue
        prefix = names.get(kicker["profile_gender"])
        if not prefix:
            continue
        try:
            if not member.nick:
                await member.edit(nick=prefix.format(username=member.name))
            elif not "kicker" in member.nick.lower():
                await member.edit(nick=prefix.format(username=member.nick))
        except discord.DiscordException:
            continue


@tasks.loop(seconds=30)
async def check_success_top_up_balance():
    users: Dict[str, Dict[str, int]] = custom_cache.get_all_top_up_users()
    for user_id, balance_and_attempt in users.items():
        try:
            user = bot.get_user(int(user_id))
        except:
            continue
        if not user:
            continue
        wallet = await get_server_wallet_by_discord_id(user.id)
        if not wallet:
            continue
        new_balance = get_usdt_balance(wallet)
        if new_balance > balance_and_attempt["balance"]:
            message = translations["balance_topped_up_message"]["en"].format(
                amount=new_balance - balance_and_attempt["balance"],
                wallet=wallet
            )
            try:
                await user.send(
                    embed=discord.Embed(
                        colour=discord.Colour.green(),
                        description=message,
                        title="Thanks!"
                    )
                )
            finally:
                custom_cache.delete_top_up(user_id)
        else:
            custom_cache.retry_top_up(user_id)


@tasks.loop(hours=24)
async def create_leaderboard():
    for guild_id in GUILDS_FOR_TASKS:
        guild = bot.get_guild(guild_id)
        if not guild:
            continue
        lang = get_lang_prefix(guild.id)
        channel = await get_or_create_channel_by_category_and_name(
            guild=guild,
            category_name=LEADERBOARD_CATEGORY_NAME,
            channel_name=LEADERBOARD_CHANNEL_NAME
        )
        await channel.purge()
        now = datetime.utcnow().strftime("%m/%d/%Y")
        try:
            await channel.send(
                content=translations["points_leaderboard_message"][lang].format(
                    now=now,
                    leaderboard_url="https://app.sidekick.fans/leaderboard/points"
                )
            )
        except discord.DiscordException as e:
            await logger.error_discord(f"No permissions! {e}")
            continue
        for role in guild.roles:
            if role.name != "@everyone":
                await channel.set_permissions(role, send_messages=False)
        dto = LeaderboardDatabase()
        leaders: List[dict] = await dto.all()
        for leader in leaders:
            name: str = leader["username"]
            position: int = leader["total_pos"]
            score: int = leader["total_score"]
            image_url : str= leader["public_link"]
            embed = discord.Embed(
                colour=discord.Colour.blue(),
                title=f"TOP {position}. **{name}**",
                description=translations["leaderboard_score"][lang].format(score=score)
            )
            embed.set_thumbnail(url=image_url)
            await channel.send(embed=embed)

@tasks.loop(hours=12)
async def send_message_for_get_coupon():
    for guild in bot.guilds:
        try:
            lang = get_lang_prefix(guild.id)
            lobby_channel = await get_or_create_channel_by_category_and_name(
                category_name=GUIDE_CATEGORY_NAME,
                channel_name=GUIDE_CHANNEL_NAME,
                guild=guild
            )
            embed = discord.Embed(
                title=translations["coupon_announcement_message_title"][lang],
                description=translations["coupon_announcement_message"][lang],
                color=discord.Color.green()
            )
            view = BaseView(timeout=12 * 60 * 60)
            view.add_item(CreateWalletButton(lang=lang))
            await lobby_channel.send(embed=embed, view=view)
        except Exception as e:
            logger.error("Coupon error: " + str(e))

@bot.event
async def on_member_join(member):
    user_info = custom_cache.get_user_invite(member.id)
    if user_info:
        channel_name = user_info["channel_name"]
        invite_link = user_info["invite_link"]
        guild_id = user_info["guild_id"]
        guild = bot.get_guild(guild_id)
        lang = get_lang_prefix(guild.id)
        private_channel = discord.utils.get(guild.voice_channels, name=channel_name)
        if private_channel is None:
            await member.send(translations["private_channel_deleted"][lang])
            return
        if private_channel:
            try:
                await private_channel.set_permissions(member, read_messages=True)
                await member.send(translations["private_channel_invite"][lang].format(invite_link=invite_link))
            except discord.Forbidden:
                await logger.error_discord(
                    f"Error: Bot does not have permission to set permissions for the channel '{channel_name}' in guild '{guild.name}' or Unable to send a DM to {member.name}"
                )
            except discord.HTTPException as http_error:
                await logger.error_discord(
                    f"HTTPException: Failed to set permissions for the member in '{channel_name}' due to an HTTP error: {http_error} or Failed to send a message to {member.name}"
                )
