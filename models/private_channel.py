import discord
import asyncio

from bot_instance import get_bot
from config import CUSTOMER_SUPPORT_TEAM_IDS, MAIN_GUILD_ID
from message_tasks import start_all_messages
from database.dto.psql_services import Services_Database
from database.dto.sql_profile import Profile_Database
from background_tasks import (
    send_message_after_2_min,
    send_message_after_5_min,
)
from services.messages.customer_support_messenger import send_message_to_customer_support
from views.done_button import DoneButton

main_guild_id = MAIN_GUILD_ID
bot = get_bot()


async def create_private_discord_channel(bot_instance, guild_id, channel_name, challenger, challenged, serviceName, kicker_username, base_category_name = "Sidekick Chatrooms"):
    guild = bot.get_guild(guild_id)

    services_db = Services_Database()
    kickers = await services_db.get_kickers()
    managers = await services_db.get_managers()

    kicker_members = []
    for kicker_id in kickers:
        kicker = guild.get_member(kicker_id)
        if kicker:
            kicker_members.append(kicker)
        else:
            print(f"Kicker with ID {kicker_id} not found in the guild.")

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

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        challenger: discord.PermissionOverwrite(read_messages=True),
        challenged: discord.PermissionOverwrite(read_messages=True)
    }

    if challenged in kicker_members:
        for kicker in kicker_members:
            overwrites[kicker] = discord.PermissionOverwrite(read_messages=True)

    channel = await category.create_voice_channel(channel_name, overwrites=overwrites)

    invite = await channel.create_invite(max_age=86400)

    await channel.send(
        f"Welcome to the Sidekick Private Session Room!\n" +
        "We hope you enjoy the games and the time spent together ❤️.\n" +
        f"If anything goes wrong, please create a ticket in our <#1233350206280437760> channel!\n" +
        f"Your Kicker's username is @{kicker_username}"
    )
    
    await start_all_messages(channel)
    
    kicker_message = (f"Hey @{kicker_username}! Your session has started. Please check this private channel: {invite.url}.")

    manager_message = (f"Hey! Session between kicker: @{kicker_username} and {challenger.name} has started. Please check this private channel: {invite.url}.")

    user_message = (f"Your session {challenger.name} with @{kicker_username} is ready!\n" +
                    f"In case the kicker is inactive in the private channel, you can reach out to the user via discord username @{challenged.name}.\n"+
                    f"Join the private channel between you and the kicker: {invite.url}\n" +
                    "**Important: If you did not receive a session, please create a ticket to report this case and get refded <#1233350206280437760>**")
    
    manager_members = []

    try:
        await challenger.send(user_message)
        if challenged.id != 1208433940050874429:
            await challenged.send(kicker_message)
        
        if challenged in kicker_members:
            for manager_id in managers:
                manager = await bot.fetch_user(manager_id)
                manager_members.append(manager)
                await manager.send(manager_message)
    except discord.HTTPException:
        print("Failed to send invite links to one or more participants.")

    await send_message_to_customer_support(bot, manager_message)

    if challenged in kicker_members:
        if send_message_after_2_min.is_running():
            print("Task 2 minutes send message is already running, stopping it first.")
            send_message_after_2_min.cancel()
            await asyncio.sleep(0.1) 
        if send_message_after_5_min.is_running():
            print("Task 5 minutes send message is already running, stopping it first.")
            send_message_after_5_min.cancel()
            await asyncio.sleep(0.1)
            
        await send_message_after_2_min.start(manager_members, challenged, kicker_username, invite.url)
        await send_message_after_5_min.start(manager_members, challenged, kicker_username, invite.url)
    
    # Special handling for the specific user ID
    if challenged.id == 1208433940050874429:
        # Creating the embed
        embed = discord.Embed(title="👋 Hi there! Welcome to the Web3 Mastery Tutorial!", description="I'm CZ, here to guide you through your first steps into an exciting world🌐✨", color=discord.Color.blue())
        embed.add_field(name="Congratulations on successfully placing your order 🎉", value="You've just unlocked the title of \"Web3 Master,\" but the journey doesn't stop here.", inline=False)
        embed.add_field(name="Learn and Earn", value="Go through the info we’ve shared here carefully and hit the 'I’ve learnt all the acknowledgments above' button to claim your campaign POINTS.", inline=False)
        embed.add_field(name="Refund Alert", value="Remember, the $4 you spent will be refunded back to your account at the end of the campaign. Keep an eye on your balance!", inline=False)
        embed.add_field(name="More Points, More Power", value="Place more orders and boost your POINTs tally significantly.", inline=False)
        embed.add_field(name="Exploring Sidekick: All You Need to Know!", value="[Watch Here](https://youtu.be/h9fzscEdC1Y)", inline=False)
        embed.set_footer(text="Let's make your crypto journey rewarding 🚀")
        view = DoneButton()
        await channel.send(embed=embed, view=view)
    return True, channel


async def send_challenge_invites(challenger, challenged, invite_url):
    await challenger.send(f"Your session is ready! Join the private channel: {invite_url}")
    if challenged.id != challenger.id:
        await challenged.send(f"You've been challenged! Join the private channel: {invite_url}")


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

    try:
        invite = await channel.create_invite(max_age=14400)  # Create a 24-hour invite
        await send_challenge_invites(challenger, challenged, invite.url)
        return True, channel
    except discord.HTTPException:
        return False, "Failed to send invite links to one or more participants."