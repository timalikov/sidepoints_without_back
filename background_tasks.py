import asyncio
import csv
from datetime import datetime, timezone, timedelta
import discord
from bot_instance import get_bot
from discord.ext import tasks
from config import MAIN_GUILD_ID
from models.forum import get_and_recreate_forum
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
):
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
        kicker=kicker
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
):
    await asyncio.sleep(3600)
    message_embed = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=f"Hey @{customer.name}",
        description=(
            f"Has your session with kicker @{kicker.name} finished?"
        )       
    )

    view = SessionCheckView(
        customer=customer,
        kicker=kicker
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

async def send_challenge_invites(challenger, challenged, invite_url):
    await challenger.send(f"Your session is ready! Join the private channel: {invite_url}")
    if challenged.id != challenger.id:
        await challenged.send(f"You've been challenged! Join the private channel: {invite_url}")


@tasks.loop(count=1)  # Ensure this runs only once
async def revoke_channel_access(channel, member):
    await asyncio.sleep(3600)  # Sleep for one hour (3600 seconds)
    await channel.set_permissions(member, overwrite=None)  # Remove specific permissions for this member
    # print(f"Permissions revoked for {member.display_name} in channel {channel.name}.")


async def join_or_create_private_discord_channel(bot, guild_id, challenge, challenger, challenged):
    guild = bot.get_guild(guild_id)

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
        success, channel = await create_private_discord_channel(bot, guild_id, challenge, channel_name, challenger, challenged, base_category_name="Sidekick Team Rooms")
        if not success:
            return False, "Failed to create a new private channel"
        await Profile_Database.add_channel_to_user(challenged.id, channel.id)

    await channel.set_permissions(challenger, read_messages=True)
    await channel.set_permissions(challenged, read_messages=True)

    # Start the revocation task
    revoke_channel_access.start(channel, challenger)
    # Create an invite and send to both challenger and challenged
    try:
        invite = await channel.create_invite(max_age=14400)  # Create a 24-hour invite
        await send_challenge_invites(challenger, challenged, invite.url)
        return True, channel
    except discord.HTTPException:
        return False, "Failed to send invite links to one or more participants."
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

