import asyncio
import csv
from datetime import datetime, timezone, timedelta
from typing import Any
import discord
from bot_instance import get_bot
from discord.ext import tasks
from config import MAIN_GUILD_ID
from models.forum import get_and_recreate_forum
from services.sqs_client import SQSClient
from views.refund_replace import RefundReplaceView
from database.dto.sql_profile import Profile_Database
from database.dto.psql_services import Services_Database
from views.session_check import SessionCheckView

main_guild_id = MAIN_GUILD_ID
bot = get_bot()

@tasks.loop(count=1)
async def session_start_check(
    *,
    customer: discord.User,
    kicker: discord.User,
    purchase_id: int,
    channel: Any
):
    print("session_start_check starting to send message")
    await asyncio.sleep(300)
    message_embed = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=f"Hey @{customer.name}",
        description=(
            f"Has your session with kicker @{kicker.name} started?"
        )       
    )

    view = SessionCheckView(
        customer=customer,
        kicker=kicker,
        purchase_id=purchase_id,
        channel=channel,
    )
    await customer.send(
        view=view,
        embed=message_embed
    )

@tasks.loop(count=1)
async def session_delivery_check(
    *,
    customer: discord.User,
    kicker: discord.User,
    purchase_id: int,
    channel: Any,
):
    ONE_HOUR: int = 3600
    await asyncio.sleep(ONE_HOUR)
    message_embed = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=f"Hey @{customer.name}",
        description=(
            f"Has your session with kicker @{kicker.name} delivered?"
        )       
    )

    view = SessionCheckView(
        customer=customer,
        kicker=kicker,
        purchase_id=purchase_id,
        channel=channel,
    )
    await customer.send(
        view=view,
        embed=message_embed
    )

@tasks.loop(seconds=20, count=4)
async def send_user_refund_replace(
    *,
    customer: discord.User,
    kicker: discord.User,
    purchase_id: int,
    channel: Any = None,
    invite_url: str = None,
    stop_event: asyncio.Event
):
    if stop_event.is_set():
        print("send_user_refund_replace task stopped.")
        send_user_refund_replace.cancel()
        return
    
    sqs_client = SQSClient()
    
    print("send_user_refund_replace starting to send message")
    message_embed = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=f"The kicker has not responded yet",
        description=(
            f"Would you like a refund or replace the kicker?"
        )       
    )

    view = RefundReplaceView(
        customer=customer,
        kicker=kicker,
        purchase_id=purchase_id,
        sqs_client=sqs_client,
        channel=channel,
        stop_task=stop_event.set
    )
    await customer.send(
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
    services_db = Services_Database()
    for guild in bot.guilds:
        try:
            forum_channel: discord.channel.ForumChannel = await get_and_recreate_forum(guild)
        except discord.DiscordException:
            return
        forum_channel.overwrites[guild.default_role].read_messages = False
        await services_db.start_posting(
            forum_channel=forum_channel, guild=guild, bot=bot
        )
        forum_channel.overwrites[guild.default_role].read_messages = True

