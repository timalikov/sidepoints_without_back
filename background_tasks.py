import os
import asyncio
import csv
from datetime import datetime, timezone, timedelta
import discord
from discord import ForumTag
from discord.ui import View
from bot_instance import get_bot
from discord.ext import tasks
from button_constructors import ShareButton, ChatButton
from config import MAIN_GUILD_ID, APP_CHOICES, CATEGORY_TO_TAG
from models.forum import create_base_forum
from sql_forum_server import ForumsOfServerDatabase
from sql_profile import Profile_Database
from sql_forum_posted import ForumUserPostDatabase  # Import the ForumUserPostDatabase class
from database.psql_services import Services_Database
from serializers.profile_serializer import serialize_profile_data

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

async def create_private_discord_channel(bot_instance, guild_id, channel_name, challenger, challenged, serviceName, kickerUsername, base_category_name = "Sidekick Chatrooms"):
    guild = bot.get_guild(guild_id)

    services_db = Services_Database()
    kickers = await services_db.get_kickers()
    managers = await services_db.get_managers()

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

    channel = await category.create_voice_channel(channel_name, overwrites=overwrites)

    invite = await channel.create_invite(max_age=86400)

    await channel.send(f"Welcome to the Side Quest Private Session Room!\n" +
                       # f"Your payment of ${challenge['price']} has been processed, and you can now arrange the perfect time for a game!\n" +
                       # f"The game is scheduled for {game_date}.\n" +
                       "We hope you enjoy the games and the time spent together ❤️.\n" +
                       f"If anything goes wrong, please create a ticket in our <#1233350206280437760> channel! Enjoy!")
    
    kicker_message = (f"Hey @{kickerUsername}! Your session has started. Please check this private channel: {invite.url}.")

    manager_message = (f"Hey! Session between kicker: @{kickerUsername} and {challenger.name} has started. Please check this private channel: {invite.url}.")

    user_message = (f"Your session {challenger.name} with @{kickerUsername} is ready!" +
                    f"In case the kicker is inactive in the private channel, you can reach out to the user via discord username @{challenged.name}.\n"+
                    f"Join the private channel between you and the kicker: {invite.url}")
    
    message_after_2_min = (f"Hey @{kickerUsername}! It's been 2 minutes since the session started. If you haven't responded yet, please check the private channel: {invite.url}.")

    message_after_5_min = (f"Hey @{kickerUsername}! It's been 5 minutes since the session started. If you haven't responded yet, please check the private channel: {invite.url}.")

    kicker_members = []
    manager_members = []

    for kicker_id in kickers:
        kicker = guild.get_member(kicker_id)
        if kicker:
            kicker_members.append(kicker)
        else:
            print(f"Kicker with ID {kicker_id} not found in the guild.")
    
    for manager_id in managers:
        manager = await bot.fetch_user(manager_id)
        if manager:
            manager_members.append(manager)
        else:
            print(f"Manager with ID {manager_id} not found in the guild.")
    
    if challenged in kicker_members:
        for kicker in kicker_members:
            overwrites[kicker] = discord.PermissionOverwrite(read_messages=True)

    try:
        await challenger.send(user_message)
        if challenged.id != 1208433940050874429:
            await challenged.send(kicker_message)
        for manager in manager_members:
            await manager.send(manager_message)
    except discord.HTTPException:
        print("Failed to send invite links to one or more participants.")

    send_message_after_2_min.start(manager_members, challenged, message_after_2_min)
    send_message_after_5_min.start(manager_members, challenged, message_after_5_min)
  

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

first_message_2_min = True
@tasks.loop(minutes=2)
async def send_message_after_2_min(managers, challenged, message_after_2_min):
    global first_message_2_min
    if not first_message_2_min:
        try:
            await challenged.send(message_after_2_min)
            for manager in managers:
                await manager.send(message_after_2_min)
            send_message_after_2_min.stop()
        except discord.HTTPException as e:
            print(f"Failed to send message to {manager.name}: {e}")
    else:
        first_message_2_min = False

first_message_5_min = True
@tasks.loop(minutes=5)
async def send_message_after_5_min(managers, challenged, message_after_5_min):
    global first_message_5_min
    if not first_message_5_min:
        try:
            await challenged.send(message_after_5_min)
            for manager in managers:
                await manager.send(message_after_5_min)
            send_message_after_5_min.stop()
        except discord.HTTPException as e:
            print(f"Failed to send message to {manager.name}: {e}")
    else:
        first_message_5_min = False
    
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

class UserProfileView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)
        self.profile_data = serialize_profile_data(user_data)
        self.user_id = user_data['discord_id']
        self.task_id = user_data['service_type_id']
        button = discord.ui.Button(label="Go", style=discord.ButtonStyle.primary, custom_id=f"go_{self.user_id}")
        button.callback = self.button_callback  # Set the callback for the button
        self.add_item(button)  # Add the button to the view
        self.add_item(ShareButton(self.user_id))
        self.add_item(ChatButton(self.user_id))


    async def button_callback(self, interaction: discord.Interaction):

        serviceId = self.profile_data['service_id']
        discordServerId = interaction.guild.id
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{serviceId}?discordServerId={discordServerId}"
        try:
            await interaction.response.send_message(
                f"To participate in this session, please complete your payment here: {payment_link}",
                ephemeral=True
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                f"To participate in this session, please complete your payment here: {payment_link}",
                ephemeral=True
            )
        except discord.errors.HTTPException as e:
            print(f"HTTPException: {e}")
        except Exception as e:
            print(f"Unhandled exception: {e}")

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


class Post_FORUM:
    def __init__(self, bot, profile_data, forum_channel, thread=False):
        self.bot = bot
        self.forum_channel: discord.ForumChannel = forum_channel
        self.forum_id: int = forum_channel.id
        self.guild_id: int = str(forum_channel.guild.id)
        self.profile_data: dict = serialize_profile_data(profile_data)
        self.thread: discord.Thread = thread

    async def post_user_profile(self):
        category = self.profile_data['service_title']
        serviceTypeId = self.profile_data['service_type_id']
        task_id = APP_CHOICES.get(serviceTypeId, "Coaching")

        embed = discord.Embed(
            title=self.profile_data['profile_username'],
            description=f"Discord username: <@{int(self.profile_data['discord_id'])}>\n\n {self.profile_data['service_description']}"
        )

        embed.set_image(url=self.profile_data['service_image'])
        embed.add_field(name="Price", value=f"${self.profile_data['service_price']}/hour", inline=True)
        embed.add_field(name="Category", value=self.profile_data.get('service_title', f'{category}'), inline=True)
        view = UserProfileView(self.profile_data)

        tag_name = self.profile_data["service_type_name"]
        tag = discord.utils.get(self.forum_channel.available_tags, name=tag_name)
        if not tag:
            tag = discord.ForumTag(name=tag_name)
            new_tags = list(self.forum_channel.available_tags)
            new_tags.append(tag)
            self.forum_channel.edit(available_tags=new_tags)

        if self.thread:
            first_message = await self.thread.fetch_message(self.thread.id)
            await self.thread.add_tags(tag)
            await first_message.edit(embed=embed, view=view)
        else:
            thread_result = await self.forum_channel.create_thread(
                name=f"Profile: <@{self.profile_data['profile_username']}>",
                content="Click 'Go' to interact with this profile!",
                embed=embed,
                view=view,
                reason="Automated individual profile showcase",
                applied_tags=[tag] if tag else [],
                auto_archive_duration=60,
                allowed_mentions=discord.AllowedMentions.none()
            )
            thread_id = thread_result.thread.id
            await ForumUserPostDatabase.add_forum_post(self.forum_id, thread_id, self.profile_data['discord_id'],
                                                       self.guild_id)
            await asyncio.sleep(4)
            return True


@tasks.loop(hours=24)
async def post_user_profiles():
    bot = get_bot()  # Assuming you have a function to get your bot instance
    services_db = Services_Database()

    guild_ids = [guild.id for guild in bot.guilds]

    for guild_id in guild_ids:
        for i in range(100):  # Limit to first 100 users
            profile_data = await services_db.get_next_service()
            if not profile_data:
                break
            guild = bot.get_guild(guild_id)
            existing_thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(
                profile_data['discord_id'],
                str(guild_id)
            )
            try:
                if existing_thread_id:
                    thread = await guild.fetch_channel(int(existing_thread_id))
                    if thread.archived:
                        await thread.edit(archived=False)
                    forum_channel = thread.parent
                    temp_post = Post_FORUM(bot, profile_data, forum_channel, thread)
                    await temp_post.post_user_profile()
                else:
                    forum_list_id = await ForumsOfServerDatabase.get_forums_by_server(int(guild_id))
                    posted_check = False
                    for val in forum_list_id:
                        forum_channel = bot.get_channel(int(val))
                        list_of_threads = forum_channel.threads
                        if len(list_of_threads) <= 1000:
                            temp_post = Post_FORUM(bot, profile_data, forum_channel, False)
                            await temp_post.post_user_profile()
                            posted_check = True
                    if not posted_check:
                        new_forum_channel = await create_base_forum(guild)
                        await ForumsOfServerDatabase.add_forum(str(guild_id), str(new_forum_channel.id))
                        temp_post = Post_FORUM(bot, profile_data, new_forum_channel, False)
                        await temp_post.post_user_profile()
            except Exception as e:
                pass
