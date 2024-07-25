import asyncio
import csv
from datetime import datetime, timezone, timedelta
import discord
from discord import ForumTag
from discord.ui import View
from bot_instance import get_bot
from discord.ext import tasks
from button_constructors import ShareButton, ChatButton
from config import MAIN_GUILD_ID, FORUM_ID, APP_CHOICES, LEADER_BOT_CHANNEL, CATEGORY_TO_TAG, LEADER_BOT_CHANNEL_LIST
from getServices import DiscordServiceFetcher
# from play_view import PlayView
# from sql_challenge import SQLChallengeDatabase
from sql_forum_server import ForumsOfServerDatabase
from sql_profile import Profile_Database
from sql_forum_posted import ForumUserPostDatabase  # Import the ForumUserPostDatabase class

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
    channel = await category.create_text_channel(channel_name, overwrites=overwrites)

    invite = await channel.create_invite(max_age=86400)

    await channel.send(f"Welcome to the Side Quest Private Session Room!\n" +
                       # f"Your payment of ${challenge['price']} has been processed, and you can now arrange the perfect time for a game!\n" +
                       # f"The game is scheduled for {game_date}.\n" +
                       "We hope you enjoy the games and the time spent together ❤️.\n" +
                       f"If anything goes wrong, please create a ticket in our <#1233350206280437760> channel! Enjoy!")
    kicker_message = f"Hey {kickerUsername}, {challenger.name} has purchased {serviceName} session with you! Join the private channel between you and the user: {invite.url} to complete the session."
    user_message = f"Your session {challenger.name} with {kickerUsername} is ready! Join the private channel between you and the kicker: {invite.url}"
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

class UserProfileView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)
        self.profile_data = user_data
        self.user_id = user_data["discordId"]
        self.task_id = user_data["serviceTypeId"]
        button = discord.ui.Button(label="Go", style=discord.ButtonStyle.primary, custom_id=f"go_{self.user_id}")
        button.callback = self.button_callback  # Set the callback for the button
        self.add_item(button)  # Add the button to the view
        self.add_item(ShareButton(self.user_id))
        self.add_item(ChatButton(self.user_id))

    async def button_callback(self, interaction: discord.Interaction):

        serviceId = self.profile_data["serviceId"]
        discordServerId = interaction.guild.id
        # payment_link = f"https://sidekick.fans/payment/test"
        # payment_link = f"https://app.sidekick.fans/services/{serviceId}?discordServerId={discordServerId}"
        payment_link = f"https://apptest.sidekick.fans/payment/{serviceId}?discordServerId={discordServerId}"
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
        writer.writerow([])  # Write an empty row to clear the file
    # print("posted_user_ids.csv cleared successfully.")


class Post_FORUM:
    def __init__(self, bot, profile_data, forum_channel, thread=False):
        self.bot = bot
        self.forum_channel = forum_channel
        self.forum_id = forum_channel.id
        self.guild_id = str(forum_channel.guild.id)
        self.profile_data = profile_data
        self.thread = thread
    async def post_user_profile(self):
        category = self.profile_data["serviceTitle"]
        serviceTypeId = self.profile_data["serviceTypeId"]
        task_id = APP_CHOICES.get(serviceTypeId, "Coaching")

        embed = discord.Embed(
            title=self.profile_data['profileUsername'],
            description=f"Discord username: <@{int(self.profile_data['discordId'])}>\n\n {self.profile_data['serviceDescription']}"
        )
        # embed.set_author(name=f"@{self.profile_data['discord_username']}", url=f"https://discord.com/users/{self.profile_data['user_id']}")
        embed.set_image(url=self.profile_data['serviceImage'])
        embed.add_field(name="Price", value=f"${self.profile_data['servicePrice']}/hour", inline=True)
        embed.add_field(name="Category", value=self.profile_data.get('serviceTitle', f'{category}'), inline=True)
        view = UserProfileView(self.profile_data)

        tag_name = CATEGORY_TO_TAG.get(serviceTypeId)
        # print("The tag name: ", tag_name)
        tag = discord.utils.get(self.forum_channel.available_tags, name=tag_name)
        if self.thread:
            first_message = await self.thread.fetch_message(self.thread.id)
            await first_message.edit(embed=embed, view=view)
            # print(f"Thread with profile for {self.profile_data['profileUsername']} updated successfully. Thread ID: {self.thread.id}")
        else:
            # If the thread does not exist, create a new one
            thread_result = await self.forum_channel.create_thread(
                name=f"Profile: <@{self.profile_data['profileUsername']}>",
                content="Click 'Go' to interact with this profile!",
                embed=embed,
                view=view,
                reason="Automated individual profile showcase",
                applied_tags=[tag] if tag else None,
                auto_archive_duration=60,
                allowed_mentions=discord.AllowedMentions.none()
            )
            thread_id = thread_result.thread.id
            await ForumUserPostDatabase.add_forum_post(self.forum_id, thread_id, self.profile_data["discordId"], self.guild_id)
            # print(f"Thread with profile for {self.profile_data['profileUsername']} posted successfully. Thread ID: {thread_id}")
            await asyncio.sleep(4)
            return True

@tasks.loop(hours=24)
async def post_user_profiles():
    # print("It started")
    # all_user_ids = await Profile_Database.get_all_users_with_priority()

    userData = DiscordServiceFetcher()
    userData.fetch_services()
    guild_ids = [1208438041174343690]
    # guild_ids = [805397679319810088]
    for guild_id in guild_ids:
        # print("It is posting")
        for i in range(0, userData.total_elements):
            guild = bot.get_guild(guild_id)
            profile_data = userData.get_next()
            # print(profile_data)
            existing_thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(profile_data["discordId"], str(guild_id))
            try:
                if existing_thread_id:
                    # print("Exist thread")
                    thread = await guild.fetch_channel(int(existing_thread_id))

                    # Modification: Unarchive the thread if it is archived
                    if thread.archived:
                        await thread.edit(archived=False)

                    forum_channel = thread.parent
                    temp_post = Post_FORUM(bot, profile_data, forum_channel, thread)
                    await temp_post.post_user_profile()
                else:
                    # print("Hi all 2")
                    forum_list_id = await ForumsOfServerDatabase.get_forums_by_server(int(guild_id))
                    # print("The forum_list_id:", forum_list_id)
                    posted_check = False
                    for val in forum_list_id:
                        forum_channel = bot.get_channel(int(val))
                        list_of_threads = forum_channel.threads
                        if len(list_of_threads) <= 1000:
                            # print('Less than 1000')
                            # print("The bot:", bot)
                            # print("The profile data:", profile_data)
                            # print("The forum channel:", forum_channel)
                            temp_post = Post_FORUM(bot, profile_data, forum_channel, False)
                            # print("The temp post:", temp_post)
                            await temp_post.post_user_profile()
                            posted_check = True
                    if posted_check == False:
                        # print("New categorry")
                        base_category_name = "sidekick-card-category"
                        category = None
                        index = 1
                        while not category:
                            category_name = f"{base_category_name}-{index}"
                            category = discord.utils.get(guild.categories, name=category_name)
                            if category and len(category.channels) >= 50:
                                category = None
                                index += 1
                            elif not category:
                                category = await guild.create_category(category_name)
                        # print("I am here URAAA")
                        values_list = list(CATEGORY_TO_TAG.values())
                        available_tags = [ForumTag(name=tag) for tag in values_list]
                        forum_ids = await ForumsOfServerDatabase.get_forums_by_server(server_id=str(guild_id))

                        name_len = len(forum_ids)
                        # print("The length:", name_len)
                        new_channel_name = f"SideKick Cards {name_len}"
                        # print("The channel name:", name_len)
                        # print("The available tags: ", available_tags)
                        # print("The guild:", guild)
                        new_forum_channel = await guild.create_forum(
                            name=new_channel_name,
                            topic="SideKickers Cards",
                            category=category,
                            available_tags=available_tags,
                            overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False)}
                        )

                        # print("This is the new forum:", new_forum_channel)
                        await ForumsOfServerDatabase.add_forum(str(guild_id), str(new_forum_channel.id))
                        temp_post = Post_FORUM(bot, profile_data, new_forum_channel, False)
                        await temp_post.post_user_profile()
            except Exception as e:
                pass
                # print(f"Failed to post or update profile for {profile_data['profileUsername']}: {e}")


# @tasks.loop(hours=24)
# async def post_weekly_leaderboard():
#     leaderboard = await SQLChallengeDatabase.get_leaderboard('week')
#     if not leaderboard:
#         print("Leaderboard is empty. No data to post.")
#         return
#
#     # Determine the maximum length of the names and points for padding
#     max_name_length = max(len(entry['name']) for entry in leaderboard)
#     max_points_length = max(len(f"{entry['points']:.2f}") for entry in leaderboard)
#     embeds = []
#     for idx, entry in enumerate(leaderboard):
#         place = f"{idx + 1}".rjust(2)  # Right justify the place number
#         name_padded = entry['name'].ljust(max_name_length)
#         points_padded = f"{entry['points']:.2f}".rjust(max_points_length)
#         description = f"```Place: {place}  \nName: {name_padded}  Credits: {points_padded}```"
#         embed = discord.Embed(description=description, color=discord.Color.blue())
#         embed.set_thumbnail(url=entry['user_picture'])
#         embeds.append(embed)
#     for i in LEADER_BOT_CHANNEL_LIST:
#         channel = bot.get_channel(i)
#         allowed_mentions = discord.AllowedMentions.none()
#         if channel:
#             # Send the leaderboard embeds in batches of 10
#             for i in range(0, len(embeds), 10):
#                 batch = embeds[i:i+10]
#                 batch_range = f"\n## **Leaderboard from #{i + 1} to #{i + len(batch)}**"
#                 await channel.send(content=batch_range, allowed_mentions=allowed_mentions)
#                 await channel.send(embeds=batch, allowed_mentions=allowed_mentions)
#             print("Weekly leaderboard posted successfully.")
#         else:
#             print("Leaderboard channel not found.")
