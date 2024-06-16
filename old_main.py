# from sql_profile import Profile_Database
# import asyncio
#
# async def fetch_user_data(username):
#     print(username)
#     print(username.strip().lower())
#     user_data_list = await Profile_Database.get_user_data_by_username(username)
#     return user_data_list
#
# # Your username
# username = "爱唱歌小兰"
#
# print(username)
# print(username.strip().lower())
#
# # Create an event loop to run the async function
# loop = asyncio.get_event_loop()
# user_data_list = loop.run_until_complete(fetch_user_data(username))
#
# # Print or process the fetched user data
# print(user_data_list)

# import asyncio
# import discord
# from discord import app_commands
# from discord.ui import View
# import random
# from sql_challenge import SQLChallengeDatabase
# from discord.ext import commands, tasks
# from play_view import PlayView
# from profile_view import ProfileView
# from sql_profile import Profile_Database
# from dotenv import load_dotenv
# import os
# from flask import Flask, request, jsonify, Response
# import threading
# import web3_test
# from multiprocessing import Process
# import csv
# import io
# from datetime import datetime, timedelta, timezone  # Import timezone explicitly
#
# load_dotenv()
#
# # Now you can access the environment variables using os.getenv
# main_guild_id = int(os.getenv('MAIN_GUILD_ID'))
# bot_token = os.getenv('DISCORD_BOT_TOKEN')
#
# intents = discord.Intents.default()
# # Enable the message content intent
# intents.message_content = True
# intents.members = True
# # Use the updated intents in your bot definition
# bot = commands.Bot(command_prefix='!', intents=intents)
#
# ##### To get list of users who are currently online #####
# async def list_online_users(guild):
#     if guild is None:
#         return []
#     online_members = [member for member in guild.members if str(member.status) == 'online']
#     online_member_ids = [member.id for member in online_members]
#     return online_member_ids
#
# @bot.tree.command(name="profile", description="Use this command if you wish to be part of the Sidekick Playmates network.")
# async def profile(interaction: discord.Interaction):
#     guild = bot.get_guild(main_guild_id)
#     if guild is None:
#         await interaction.response.send_message("Error: Main guild not found.", ephemeral=True)
#         return
#
#     # Check if the user is a member of the guild
#     member = guild.get_member(interaction.user.id)
#     if member:
#         view = ProfileView()
#         await interaction.response.send_message("Welcome onboard!\nClick on go to profile to set up or edit your profile", view=view, ephemeral=True)
#         return
#     else:
#         await interaction.response.defer(ephemeral=True)
#         # Generate an invite link if the user is not in the guild
#         try:
#             # Create an invite that expires in 24 hours with a maximum of 10 uses
#             invite = await guild.text_channels[0].create_invite(max_age=86400, max_uses=10, unique=True)
#             await interaction.response.send_message(f"You must join our main guild to access your profile. Please join using this invite: {invite.url}", ephemeral=True)
#         except Exception as e:
#             await interaction.response.send_message("Failed to create an invite. Please check my permissions and try again.", ephemeral=True)
#             print(e)  # For debugging purposes
#
# #
# # async def play(interaction: discord.Interaction):
#
# #
# @bot.tree.command(name="go", description="Use this command and start looking for playmates!")
# @app_commands.choices(choices=[app_commands.Choice(name="All players", value=0),
#                                app_commands.Choice(name="Coaching [1 hour]", value=1),
#                                app_commands.Choice(name="Gaming Buddy [1 hour]", value=2),
#                                app_commands.Choice(name="Share a dance video [2 mins]", value=3),
#                                app_commands.Choice(name="Sing a song [3 mins]", value=4),
#                                app_commands.Choice(name="Stream Together [30 mins]", value=5),
#                                app_commands.Choice(name="Karaoke Session [30 mins]", value=6),
#                                app_commands.Choice(name="Creative Brainstorm [1 hour]", value=7),
#                                app_commands.Choice(name="Web3Class", value=101),
#                                app_commands.Choice(name="Other", value=8),
#                                ])
# async def play(interaction: discord.Interaction, choices: app_commands.Choice[int]):
#     await interaction.response.defer(ephemeral=True)
#     online_user_ids = await list_online_users(interaction.guild)
#     # all_task_user_ids = await Profile_Database.get_all_user_ids()
#     all_task_user_ids = []
#     task_id = choices.value
#     if task_id == 0:
#         all_task_user_ids = await Profile_Database.get_all_user_ids()
#     else:
#         all_task_user_ids = await Profile_Database.get_user_ids_by_task_id(task_id)
#
#     # all_task_user_ids = await Profile_Database.get_user_ids_by_task_id(choices.value)
#     if not all_task_user_ids:
#         await interaction.followup.send("Sorry, there are no players available for that task right now.", ephemeral=True)
#         return
#
#     online_task_user_ids = [uid for uid in all_task_user_ids if uid in online_user_ids]
#
#     # in case when we need to show only online
#     # all_task_user_ids = online_user_ids
#     # online_task_user_ids = online_user_ids
#
#     view = await PlayView.create(interaction.user.id, online_task_user_ids, all_task_user_ids, task_id)
#     await interaction.followup.send(embed=view.profile_info, view=view, ephemeral=True)
#
# @bot.tree.command(name="find", description="Find a user profile by their username.")
# @app_commands.describe(username="The username to find.")
# async def find(interaction: discord.Interaction, username: str):
#     username = username.strip().lower()
#     # Fetch user data based on the provided username.
#     user_data_list = await Profile_Database.get_user_data_by_username(username)  # Now correctly returns a list of dictionaries
#
#     if user_data_list:
#         # Extract user IDs from the list
#         user_ids = [user_data['user_id'] for user_data in user_data_list]
#
#         if len(user_ids) == 1 and user_ids[0] == str(interaction.user.id):
#             # print(user_ids[0])
#             # If only one user is found and it's the requester
#             await interaction.response.send_message("You cannot play by yourself, try to find another player.", ephemeral=True)
#         else:
#             # Filter out the current user's ID if they are in the list
#             other_user_ids = [user_id for user_id in user_ids if user_id != interaction.user.id]
#             if not other_user_ids:
#                 # If all user_ids are the requester's ID
#                 await interaction.response.send_message("You cannot play by yourself, try to find another player.", ephemeral=True)
#             else:
#                 # If there are other users, display them using PlayView or similar
#                 await interaction.response.defer(ephemeral=True)
#                 view = await PlayView.create(interaction.user.id, [], other_user_ids)
#                 await interaction.followup.send(embed=view.profile_info, view=view, ephemeral=True)
#     else:
#         # If no users are found, send an appropriate response.
#         await interaction.response.send_message(f"No profile found for username: {username}", ephemeral=True)

# app = Flask(__name__)
#
# @app.route('/server_user_counts', methods=['GET'])
# async def server_user_counts():
#     user_counts = {}
#     for guild in bot.guilds:
#         # Store both the guild name and member count in a dictionary as the value
#         user_counts[guild.id] = {
#             "guild_name": guild.name,
#             "member_count": guild.member_count
#         }
#     return jsonify(user_counts), 200


# class DoneButton(View):
#     def __init__(self):
#         # Setting timeout=None to make the button non-expirable
#         super().__init__(timeout=None)
#     @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
#     async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
#         # Fetch the role from the guild using the provided role ID
#         role_id = 1235556503596040224  # Role ID to be assigned
#         role = interaction.guild.get_role(role_id)
#
#         if role:
#             # Add the role to the user who clicked the button
#             try:
#                 await interaction.user.add_roles(role)
#                 await interaction.response.send_message("Good job! You've been given a special role.", ephemeral=True)
#             except discord.HTTPException as e:
#                 await interaction.response.send_message(f"Failed to assign role: {str(e)}", ephemeral=True)
#         else:
#             await interaction.response.send_message("Role not found.", ephemeral=True)

# Example function to create a private channel
# async def create_private_discord_channel(bot_instance, guild_id, challenge, channel_name, challenger, challenged, base_category_name = "Sidekick Chatrooms"):
#     guild = bot.get_guild(guild_id)
#     # Find the first available category that is not full
#     category = None
#     index = 1
#     while not category:
#         category_name = f"{base_category_name}{index}"
#         category = discord.utils.get(guild.categories, name=category_name)
#         if category and len(category.channels) >= 50:
#             category = None
#             index += 1
#         elif not category:
#             category = await guild.create_category(category_name)
#
#     # Create the private channel under the specified category
#     overwrites = {
#         guild.default_role: discord.PermissionOverwrite(read_messages=False),
#         challenger: discord.PermissionOverwrite(read_messages=True),
#         challenged: discord.PermissionOverwrite(read_messages=True)
#     }
#     channel = await category.create_text_channel(channel_name, overwrites=overwrites)
#
#     invite = await channel.create_invite(max_age=86400)
#
#     game_date = challenge['date'].date() if isinstance(challenge['date'], datetime) else challenge['date']
#
#     await channel.send(f"Welcome to the Side Quest Private Challenge Room!\n" +
#                        f"Your payment of ${challenge['price']} has been processed, and you can now arrange the perfect time for a game!\n" +
#                        f"Funds will be transferred to the other party 72 hours after the challenge date.\n" +
#                        f"The game is scheduled for {game_date}.\n" +
#                        "We hope you enjoy the games and the time spent together ❤️.\n" +
#                        f"If anything goes wrong, please create a ticket in our <#1233350206280437760> channel! Enjoy!")
#     try:
#         await challenger.send(f"You've been challenged! Join the fight private channel: {invite.url}")
#         if challenged.id != 1208433940050874429:
#             await challenged.send(f"You've been challenged! Join the fight private channel: {invite.url}")
#         print(f"Private arena text channel created: {channel.mention}. Invites sent.")
#     except discord.HTTPException:
#         print("Failed to send invite links to one or more participants.")
#
#     # Special handling for the specific user ID
#     if challenged.id == 1208433940050874429:
#         # Creating the embed
#         embed = discord.Embed(title="👋 Hi there! Welcome to the Web3 Mastery Tutorial!", description="I'm CZ, here to guide you through your first steps into an exciting world🌐✨", color=discord.Color.blue())
#         embed.add_field(name="Congratulations on successfully placing your order 🎉", value="You've just unlocked the title of \"Web3 Master,\" but the journey doesn't stop here.", inline=False)
#         embed.add_field(name="Learn and Earn", value="Go through the info we’ve shared here carefully and hit the 'I’ve learnt all the acknowledgments above' button to claim your campaign POINTS.", inline=False)
#         embed.add_field(name="Refund Alert", value="Remember, the $4 you spent will be refunded back to your account at the end of the campaign. Keep an eye on your balance!", inline=False)
#         embed.add_field(name="More Points, More Power", value="Place more orders and boost your POINTs tally significantly.", inline=False)
#         embed.add_field(name="Exploring Sidekick: All You Need to Know!", value="[Watch Here](https://youtu.be/h9fzscEdC1Y)", inline=False)
#         embed.set_footer(text="Let's make your crypto journey rewarding 🚀")
#         view = DoneButton()
#         await channel.send(embed=embed, view=view)
#     return True, channel

# async def send_challenge_invites(challenger, challenged, invite_url):
#     await challenger.send(f"You've been challenged! Join the private channel: {invite_url}")
#     if challenged.id != challenger.id:
#         await challenged.send(f"You've been challenged! Join the private channel: {invite_url}")
#
# @tasks.loop(count=1)  # Ensure this runs only once
# async def revoke_channel_access(channel, member):
#     await asyncio.sleep(3600)  # Sleep for one hour (3600 seconds)
#     await channel.set_permissions(member, overwrite=None)  # Remove specific permissions for this member
#     print(f"Permissions revoked for {member.display_name} in channel {channel.name}.")
#
# async def join_or_create_private_discord_channel(bot, guild_id, challenge, challenger, challenged):
#     guild = bot.get_guild(guild_id)
#
#     # Try to find existing channel ID from the database
#     existing_channel_ids = await Profile_Database.get_channel_id_by_user_id(challenged.id)
#     channel = None
#
#     # Check if any of the fetched channel IDs exist in the guild
#     for channel_id in existing_channel_ids:
#         channel = guild.get_channel(channel_id)
#         if channel:
#             break
#
#     channel_name = f"team-{challenged.display_name}"
#     # If no valid channel is found, create a new one
#     if not channel:
#         success, channel = await create_private_discord_channel(bot, guild_id, challenge, channel_name, challenger, challenged, base_category_name="Sidekick Team Rooms")
#         if not success:
#             return False, "Failed to create a new private channel"
#         # Add the newly created channel to the database
#         print("Challenged ID: ", challenged.id)
#         print("Channel ID: ", channel.id)
#         await Profile_Database.add_channel_to_user(challenged.id, channel.id)
#
#     await channel.set_permissions(challenger, read_messages=True)
#     await channel.set_permissions(challenged, read_messages=True)
#
#     # Start the revocation task
#     revoke_channel_access.start(channel, challenger)
#     # Create an invite and send to both challenger and challenged
#     try:
#         invite = await channel.create_invite(max_age=86400)  # Create a 24-hour invite
#         await send_challenge_invites(challenger, challenged, invite.url)
#         return True, channel.id
#     except discord.HTTPException:
#         return False, "Failed to send invite links to one or more participants."


# @app.route('/create_private_channel', methods=['POST'])
# async def handle_create_private_channel():
#     data = request.json
#     challenge_id = data.get('challenge_id')
#     if challenge_id:
#         guild = bot.get_guild(main_guild_id)
#         # Use the bot to create a private channel asynchronously
#         channel_name = f"private-channel-{challenge_id}"  # Example channel name format
#         challenge = await SQLChallengeDatabase.get_challenge(challenge_id)
#         await SQLChallengeDatabase.update_channel_created(challenge_id)
#         print(challenge['user_id1'], challenge['user_id2'])
#         second_id = int(challenge['user_id2'])
#
#         challenger = guild.get_member(int(challenge['user_id1']))
#         challenged = guild.get_member(second_id)
#
#         if not all([challenger, challenged]):
#             return jsonify({"error": "One or more users could not be found in this guild."}), 400
#         # Since this is an async function, we run it in the event loop of the bot
#
#         if challenge['task_id'] == 101:
#             future = asyncio.run_coroutine_threadsafe(join_or_create_private_discord_channel(bot, main_guild_id, challenge, challenger, challenged), bot.loop)
#         else:
#             future = asyncio.run_coroutine_threadsafe(create_private_discord_channel(bot, main_guild_id, challenge, channel_name, challenger, challenged), bot.loop)
#         success, response = future.result()  # This blocks until the coroutine completes
#
#         if success:
#             return jsonify({"message": "Private channel created", "channel_id": response}), 200
#         else:
#             return jsonify({"error": response}), 400
#     else:
#         return jsonify({"error": "Challenge ID not provided"}), 400

# @app.route('/challenges_last_week', methods=['GET'])
# def get_challenges_last_week():
#     # Get the 'days' parameter from the query string, defaulting to 7 if not provided
#     days = request.args.get('days', default=7, type=int)
#
#     # Calculate the date 'days' ago from today
#     days_ago = datetime.now() - timedelta(days=days)
#     days_ago_str = days_ago.strftime('%Y-%m-%d')
#
#     # Open database connection and prepare cursor
#     conn = SQLChallengeDatabase.get_connection()
#     cursor = conn.cursor(dictionary=True)
#
#     # SQL query to join challenges with profiles to fetch discord_username
#     query = """
#     SELECT c.challenge_id, c.user_id1, c.user_id2, c.date, c.price, c.channel_created, c.wallet, p.discord_username
#     FROM challenges c
#     LEFT JOIN profiles p ON c.user_id1 = p.user_id
#     WHERE c.date >= %s;
#     """
#     cursor.execute(query, (days_ago_str,))
#
#     # Fetch all matching records
#     challenges = cursor.fetchall()
#     cursor.close()
#     conn.close()
#
#     # Create an in-memory output file for the CSV data
#     si = io.StringIO()
#     cw = csv.writer(si)
#     # Write CSV headers including the new discord_username column
#     cw.writerow(['challenge_id', 'user_id1', 'discord_username', 'user_id2', 'date', 'price', 'channel_created', 'wallet'])
#     # Write data rows including the fetched discord_username
#     for challenge in challenges:
#         cw.writerow([
#             challenge['challenge_id'],
#             challenge['user_id1'],
#             challenge['discord_username'],
#             challenge['user_id2'],
#             challenge['date'],
#             challenge['price'],
#             challenge['channel_created'],
#             challenge['wallet']
#         ])
#
#     # Set the output file to return as an attachment
#     output = Response(si.getvalue(), mimetype='text/csv')
#     output.headers["Content-Disposition"] = "attachment; filename=challenges_since_{days}_days_ago.csv".format(days=days)
#     return output

# @tasks.loop(minutes=30)  # Checks every 2 hours
# async def delete_old_channels():
#     guild = bot.get_guild(main_guild_id)
#     if guild is None:
#         print("Guild not found")
#         return
#
#     # Retrieve all categories that match the naming pattern "Sidekick ChatroomsX"
#     chatroom_categories = [cat for cat in guild.categories if cat.name.startswith("Sidekick Chatrooms")]
#     current_time = datetime.utcnow().replace(tzinfo=timezone.utc)  # Current time in UTC with timezone aware
#
#     # Iterate over each category
#     for category in chatroom_categories:
#         for channel in category.text_channels:
#             time_diff = current_time - channel.created_at
#             if time_diff > timedelta(hours=2):  # Checking if the channel is older than 2 hours
#                 print(f"Deleting channel {channel.name} as it is older than 2 hours.")
#                 await channel.delete(reason="Cleanup: Channel older than 2 hours.")

# class UserProfileView(discord.ui.View):
#     def __init__(self, user_id):
#         super().__init__()
#         self.user_id = user_id  # Store user_id to use in the callback
#         button = discord.ui.Button(label="Go", style=discord.ButtonStyle.primary, custom_id=f"go_{user_id}")
#         button.callback = self.button_callback  # Set the callback for the button
#         self.add_item(button)  # Add the button to the view
#
#     async def button_callback(self, interaction: discord.Interaction):
#         # Fetch profile data for the user_id
#         profile_data = await Profile_Database.get_user_data(self.user_id)
#         if profile_data:
#             user_id1 = interaction.user.id
#             user_id2 = profile_data['user_id']
#             price = profile_data['price']
#             wallet = profile_data.get("wallet", "not provided")  # Ensure wallet is fetched or default
#
#             # Create a challenge in the database
#             challenge_id = await SQLChallengeDatabase.create_challenge(
#                 user_id1,
#                 user_id2,
#                 datetime.now().strftime("%d-%m-%Y"),
#                 price,
#                 wallet,
#                 interaction.guild_id
#             )
#
#             payment_link = f"https://sidekick.fans/payment/{challenge_id}"
#             # Check if initial response is done, then follow up
#             if interaction.response.is_done():
#                 await interaction.followup.send(
#                     f"To participate in this challenge, please complete your payment here: {payment_link}",
#                     ephemeral=True
#                 )
#             else:
#                 await interaction.response.send_message(
#                     f"To participate in this challenge, please complete your payment here: {payment_link}",
#                     ephemeral=True
#                 )


# posted_user_ids_file = 'posted_user_ids.csv'  # Define the filename at the top
# def load_posted_user_ids():
#     try:
#         with open(posted_user_ids_file, mode='r', newline='') as file:
#             reader = csv.reader(file)
#             return {rows[0]: rows[1] for rows in reader}  # Create a dict of user IDs to thread IDs
#     except FileNotFoundError:
#         return {}  # Return an empty dict if the file does not exist
#
# def save_posted_user_id(user_id, thread_id):
#     with open(posted_user_ids_file, mode='a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([user_id, thread_id])  # Save both user_id and thread_id
# @tasks.loop(hours=24)
# async def post_user_profiles():
#     print("Checking for new profiles to post...")
#     posted_user_ids = load_posted_user_ids()  # Load posted user IDs from CSV file
#
#     all_user_ids = await Profile_Database.get_all_user_ids()
#     selected_ids = random.sample(all_user_ids, min(len(all_user_ids), 3))
#
#     forum_channel = bot.get_channel(1237033746327273522)
#     if isinstance(forum_channel, discord.ForumChannel):
#         for user_id in selected_ids:
#             if user_id not in posted_user_ids:
#                 profile_data = await Profile_Database.get_user_data(user_id)
#                 if profile_data:
#                     embed = discord.Embed(title=profile_data['name'], description=profile_data['about'])
#                     embed.set_image(url=profile_data['user_picture'])
#                     embed.add_field(name="Price", value=f"${profile_data['price']}/hour", inline=True)
#                     embed.add_field(name="Category", value=profile_data.get('category', 'N/A'), inline=True)
#
#                     view = UserProfileView(user_id)
#
#                     try:
#                         thread_result = await forum_channel.create_thread(
#                             name=f"Profile: {profile_data['name']}",
#                             content="Click 'Go' to interact with this profile!",
#                             embed=embed,
#                             view=view,
#                             reason="Automated individual profile showcase"
#                         )
#                         thread_id = thread_result.thread.id  # Correctly access the thread ID
#                         print(f"Thread with profile for {profile_data['name']} posted successfully. Thread ID: {thread_id}")
#                         posted_user_ids[user_id] = thread_id
#                         save_posted_user_id(user_id, thread_id)  # Save new posted user ID to CSV with thread ID
#                     except Exception as e:
#                         print(f"Failed to post profile for {profile_data['name']}: {e}")
#                 else:
#                     print(f"No profile data found for user ID {user_id}")
#             else:
#                 print(f"Profile for user ID {user_id} has already been posted under Thread ID {posted_user_ids[user_id]}.")
#     else:
#         print("Forum channel not found or not a forum.")

# @bot.event
# async def on_ready():
#     delete_old_channels.start()
#     # post_user_profiles.start()
#     await bot.tree.sync()
#     await bot.tree.sync(guild=discord.Object(id=main_guild_id))
#     print(f'We have logged in as {bot.user}')
#
# def create_app():
#     return app
#
# if __name__ == "__main__":
#     bot_thread = threading.Thread(target=lambda: bot.run(bot_token))
#     bot_thread.start()
#     process = Process(target=web3_test.main)
#     process.start()
#     web3_process_pid = process.pid
#     current_process_pid = os.getpid()
#     print(f"Current process pid: {current_process_pid}, web3_process_pid: {web3_process_pid}")
#     flask_app = create_app()
#     flask_app.run(host='0.0.0.0', port=2028)



