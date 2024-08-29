from typing import Union

import os
import asyncio
import csv
from datetime import datetime, timezone, timedelta
import discord
from discord.ui import View
from bot_instance import get_bot
from discord.ext import tasks
from config import MAIN_GUILD_ID
from models.forum import get_or_create_forum
from sql_profile import Profile_Database
from database.psql_services import Services_Database

main_guild_id = MAIN_GUILD_ID
bot = get_bot()


class DoneButton(View):
    def __init__(self):
        # Setting timeout=None to make the button non-expirable
        super().__init__(timeout=None)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Fetch the role from the guild using the provided role ID
        role_ids = [1235556503596040224, 1242457735988252692]  # Role ID to be assigned
        # role = interaction.guild.get_role(role_id)

        # Fetch the first valid role from the guild using the provided role IDs
        role = None
        for role_id in role_ids:
            role = interaction.guild.get_role(role_id)
            if role:
                break

        if role:
            # Add the role to the user who clicked the button
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("Good job! You've been given a special role.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Failed to assign role: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message("Role not found.", ephemeral=True)

# Example function to create a private channel
async def create_private_discord_channel(bot_instance, guild_id, channel_name, challenger, challenged, serviceName, kickerUsername, base_category_name = "Sidekick Chatrooms"):
    guild = bot.get_guild(guild_id)
    # Find the first available category that is not full
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

    # Create the private channel under the specified category
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        challenger: discord.PermissionOverwrite(read_messages=True),
        challenged: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await category.create_voice_channel(channel_name, overwrites=overwrites)

    invite = await channel.create_invite(max_age=86400)

    await channel.send(f"Welcome to the Side Quest Private Session Room!\n" +
                       # f"Your payment of ${challenge['price']} has been processed, and you can now arrange the perfect time for a game!\n" +
                       # f"The game is scheduled for {game_date}.\n" +
                       "We hope you enjoy the games and the time spent together ❤️.\n" +
                       f"If anything goes wrong, please create a ticket in our <#1233350206280437760> channel! Enjoy!")
    kicker_message = (f"Hey {kickerUsername}, {challenger.name} has purchased {serviceName} session with you! " +
                      f"In case your user is inactive in the private channel, you can reach out to the kicker via discord username @{challenger.name}.\n" +
                      f"Join the private channel between you and the user: {invite.url} to complete the session.")

    user_message = (f"Your session {challenger.name} with {kickerUsername} is ready!" +
                    f"In case the kicker is inactive in the private channel, you can reach out to the user via discord username @{challenged.name}.\n"+
                    f"Join the private channel between you and the kicker: {invite.url}")
    try:
        # print("Kicker_message:", kicker_message)
        # print("User_message:", user_message)
        await challenger.send(user_message)
        if challenged.id != 1208433940050874429:
            await challenged.send(kicker_message)
        # print(f"Private arena text channel created: {channel.mention}. Invites sent.")
    except discord.HTTPException:
        print("Failed to send invite links to one or more participants.")

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
    print("START LOOP POST")
    bot = get_bot()  # Assuming you have a function to get your bot instance
    services_db = Services_Database()
    for guild in bot.guilds:
        try:
            forum_channel: discord.channel.ForumChannel = await get_or_create_forum(guild)
        except discord.DiscordException:
            return
        await services_db.start_posting(
            forum_channel=forum_channel, guild=guild, bot=bot
        )
