import asyncio
import csv
from datetime import datetime, timezone, timedelta
from typing import Any, List, Literal
import discord
from bot_instance import get_bot
from translate import translations, get_lang_prefix
from discord.ext import tasks
from config import (
    MAIN_GUILD_ID,
    LEADERBOARD_CATEGORY_NAME,
    LEADERBOARD_CHANNEL_NAME,
    GUILDS_FOR_TASKS,
)
from models.public_channel import get_or_create_channel_by_category_and_name
from models.forum import get_and_recreate_forum
from models.thread_forum import start_posting
from services.sqs_client import SQSClient
from views.refund_replace import RefundReplaceView
from database.dto.psql_leaderboard import LeaderboardDatabase

main_guild_id = MAIN_GUILD_ID
bot = get_bot()


@tasks.loop(seconds=20, count=4)
async def send_user_refund_replace(
    *,
    customer: discord.User,
    kicker: discord.User,
    purchase_id: int,
    channel: Any = None,
    invite_url: str = None,
    stop_event: asyncio.Event,
    lang: Literal["en", "ru"] = "en"
):
    if stop_event.is_set():
        print("send_user_refund_replace task stopped.")
        send_user_refund_replace.cancel()
        return
    
    sqs_client = SQSClient()
    
    print("send_user_refund_replace starting to send message")
    message_embed = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=translations["kicker_not_responded_yet"][lang],
        description=translations["refund_replace_prompt"][lang]
    )

    view = RefundReplaceView(
        customer=customer,
        kicker=kicker,
        purchase_id=purchase_id,
        sqs_client=sqs_client,
        channel=channel,
        stop_task=stop_event.set,
        lang=lang
    )
    view.message = await customer.send(
        view=view,
        embed=message_embed
    )

@tasks.loop(count=1)
async def send_message_after_2_min(managers, challenged, kicker_username, invite_url):
    await asyncio.sleep(120)
    message_after_2_min = (f"Hey @{kicker_username}! It's been 2 minutes since the session started. If you haven't responded yet, please check the private channel: {invite_url}.")

    try:
        await challenged.send(message_after_2_min)
        for manager in managers:
            await manager.send(message_after_2_min)
    except discord.HTTPException as e:
        print(f"Failed to send message to {manager.name}: {e}")

@tasks.loop(count=1)
async def send_message_after_5_min(managers, challenged, kicker_username, invite_url):
    await asyncio.sleep(300)
    message_after_5_min = (f"Hey @{kicker_username}! It's been 5 minutes since the session started. If you haven't responded yet, please check the private channel: {invite_url}.")
    try:
        await challenged.send(message_after_5_min)
        for manager in managers:
            await manager.send(message_after_5_min)
    except discord.HTTPException as e:
        print(f"Failed to send message to {manager.name}: {e}")


@tasks.loop(count=1)  # Ensure this runs only once
async def revoke_channel_access(channel, member):
    await asyncio.sleep(3600)  # Sleep for one hour (3600 seconds)
    await channel.set_permissions(member, overwrite=None)  # Remove specific permissions for this member
    # print(f"Permissions revoked for {member.display_name} in channel {channel.name}.")

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
                    # print(f"Deleting channel {channel.name} from guild {guild.name} as it is older than 24 hours.")
                    await channel.delete(reason="Cleanup: Channel older than 24 hours.")


posted_user_ids_file = 'posted_user_ids.csv'

async def delete_all_threads_and_clear_csv():
    for i in [1248487428872994866]:
        forum_channel = bot.get_channel(i)
        if isinstance(forum_channel, discord.ForumChannel):
            for thread in forum_channel.threads:
                await thread.delete()
            # print("All threads deleted successfully.")
        else:
            pass
            # print("Forum channel not found or not a forum.")

    # Clear the CSV file
    with open(posted_user_ids_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([])


@tasks.loop(hours=24)
async def post_user_profiles():
    await asyncio.sleep(360)
    print("START LOOP POST")
    bot = get_bot()  # Assuming you have a function to get your bot instance
    for guild in bot.guilds:
        try:
            forum_channel: discord.channel.ForumChannel = await get_and_recreate_forum(guild)
        except discord.DiscordException:
            return
        forum_channel.overwrites[guild.default_role].read_messages = False
        await start_posting(
            forum_channel=forum_channel, guild=guild, bot=bot, order_type="ASC"
        )
        forum_channel.overwrites[guild.default_role].read_messages = True


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
        except discord.DiscordException:
            print("No permissions!")
            return None
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
