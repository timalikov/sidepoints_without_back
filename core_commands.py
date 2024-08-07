from datetime import datetime

import discord
from discord import app_commands
from play_view import PlayView
from profile_view import ProfileView, WalletView
from bot_instance import get_bot
from background_tasks import delete_old_channels, post_user_profiles, delete_all_threads_and_clear_csv
from sql_subscriber import Subscribers_Database
from sql_profile import log_to_database

#post_weekly_leaderboard

#delete_all_threads_and_clear_csv
from config import MAIN_GUILD_ID, DISCORD_BOT_TOKEN
from sql_order import Order_Database
from views.boost_view import BoostView
from views.exist_service import Profile_Exist
from views.wallet_view import Wallet_exist

main_guild_id = MAIN_GUILD_ID
bot = get_bot()

##### To get list of users who are currently online #####
async def list_online_users(guild):
    if guild is None:
        return []
    online_members = [member for member in guild.members if str(member.status) == 'online']
    online_member_ids = [member.id for member in online_members]
    return online_member_ids

@bot.tree.command(name="profile", description="Use this command if you wish to be part of the Sidekick Playmates network.")
async def profile(interaction: discord.Interaction):
    # guild = bot.get_guild(main_guild_id)
    # if guild is None:
    #     await interaction.response.send_message("Error: Main guild not found.", ephemeral=True)
    #     return

    await interaction.response.defer(ephemeral=True)
    await log_to_database(interaction.user.id, "/profile")
    guild = interaction.guild
    # # Check if the user is a member of the guild
    # member = guild.get_member(interaction.user.id)
    # # Log the interaction
    # print(interaction.user.id)
    # await log_to_database(interaction.user.id, "profile")
    profile_exist = Profile_Exist(str(interaction.user.id))

    await profile_exist.initialize()

    if profile_exist.no_user:
        await interaction.followup.send("Looks like you haven't create a profile with us! Please jump to the link below and create your profile!.\nhttps://app.sidekick.fans/services/create", ephemeral=True)
    else:
        await interaction.followup.send(embed=profile_exist.profile_embed, view=profile_exist, ephemeral=True)

    # await interaction.followup.send(embed=view.profile_embed, view=view, ephemeral=True)
    # if member:
    #     # print("HE IS A MEMBER")
    #     view = ProfileView()
    #     await interaction.response.send_message("Welcome onboard!\nClick on go to profile to set up or edit your profile", view=view, ephemeral=True)
    #     return
    # else:
    #     await interaction.response.defer(ephemeral=True)
    #     # Generate an invite link if the user is not in the guildawait profile_exist.initialize()
    #     try:
    #         # Create an invite that expires in 24 hours with a maximum of 10 uses
    #         invite = await guild.text_channels[0].create_invite(max_age=86400, max_uses=10, unique=True)
    #         await interaction.response.send_message(f"You must join our main guild to access your profile. Please join using this invite: {invite.url}", ephemeral=True)
    #     except Exception as e:
    #         await interaction.response.send_message("Failed to create an invite. Please check my permissions and try again.", ephemeral=True)
    #         print(e)


async def list_all_users_with_online_status(guild):
    if guild is None:
        return []
    all_member_ids = [member.id for member in guild.members]
    # online_member_ids = [member.id for member in guild.members if str(member.status) == 'online']
    return all_member_ids

@bot.tree.command(name="go", description="Use this command and start looking for playmates!")
@app_commands.choices(choices=[app_commands.Choice(name="All players", value="ALL"),
                               app_commands.Choice(name="Buddy", value="57c86488-8935-4a13-bae0-5ca8783e205d"),
                               app_commands.Choice(name="Coaching", value="88169d78-85b4-4fa3-8298-3df020f13a6f"),
                               app_commands.Choice(name="Just Chatting", value="2974b0e8-69de-4d7c-aa4d-d5aa8e05d360"),
                               app_commands.Choice(name="Watch Youtube", value="d3ae39d2-fd86-41d7-bc38-0b582ce338b5"),
                               app_commands.Choice(name="Play Games", value="79bf303a-318b-4815-bd56-7b0b49ae7bff"),
                               app_commands.Choice(name="Virtual Date", value="d6b9fc04-bfb2-46df-88eb-6e8c149e34d9")
                               ])
async def play(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    view = PlayView(user_choice=choices.value)
    await log_to_database(interaction.user.id, "/go")

    if view.no_user:
        await interaction.followup.send(content="Sorry, there are no players.", ephemeral=True)
    else:
        await interaction.followup.send(embed=view.profile_embed, view=view, ephemeral=True)


@bot.tree.command(name="find", description="Find a user profile by their username.")
@app_commands.describe(username="The username to find.")
async def find(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    view = PlayView(user_choice="ALL", username=username)
    await log_to_database(interaction.user.id, "/find")
    if view.no_user:
        await interaction.followup.send(content="Sorry, there are no players.", ephemeral=True)
    else:
        await interaction.followup.send(embed=view.profile_embed, view=view, ephemeral=True)

async def get_guild_invite_link(guild_id):
    guild = bot.get_guild(guild_id)
    if guild:
        # Create an invite link
        invite = "https://discord.gg/sidekick"  # Expires in 1 day, 1 use
        return invite
    return None

@bot.tree.command(name="order", description="Use this command to post your service request and summon Kickers to take the order.")
@app_commands.choices(choices=[app_commands.Choice(name="All players", value="ALL"),
                               app_commands.Choice(name="Buddy", value="57c86488-8935-4a13-bae0-5ca8783e205d"),
                               app_commands.Choice(name="Coaching", value="88169d78-85b4-4fa3-8298-3df020f13a6f"),
                               app_commands.Choice(name="Just Chatting", value="2974b0e8-69de-4d7c-aa4d-d5aa8e05d360"),
                               app_commands.Choice(name="Watch Youtube", value="d3ae39d2-fd86-41d7-bc38-0b582ce338b5"),
                               app_commands.Choice(name="Play Games", value="79bf303a-318b-4815-bd56-7b0b49ae7bff"),
                               app_commands.Choice(name="Virtual Date", value="d6b9fc04-bfb2-46df-88eb-6e8c149e34d9")
                               ])
async def order(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    await log_to_database(interaction.user.id, "/order")
    await interaction.response.defer(ephemeral=True)
    order_data = {
        'user_id': interaction.user.id,
        'task_id': choices.value
    }
    await Order_Database.set_user_data(order_data)
    main_link = await get_guild_invite_link(MAIN_GUILD_ID)
    await interaction.followup.send(f"Your Kickers summon order successfully placed. \nPlease check your DM for Kicker summon responses. Please wait further instructions and join to our server using the link below\n{main_link}", ephemeral=True)


@bot.tree.command(name="subscribe", description="Use this command to post your service request and summon Kickers to take the order.")
@app_commands.choices(choices=[app_commands.Choice(name="Subscribe", value=1),
                               app_commands.Choice(name="Unsubscribe", value=0),
                               ])
async def subscribe(interaction: discord.Interaction, choices: app_commands.Choice[int]):
    await log_to_database(interaction.user.id, "/subscribe")
    await interaction.response.defer(ephemeral=True)
    if choices.value == 1:
        await Subscribers_Database.set_user_data(interaction.user.id)
        await interaction.followup.send(f"You have successfully subscribed to the order command. Each time the /order command is used by users, you will receive a notification.", ephemeral=True)
    else:
        await Subscribers_Database.delete_user_data(interaction.user.id)
        await interaction.followup.send(f"You have unsubscribed from the order command.", ephemeral=True)

@bot.tree.command(name="wallet", description="Use this command to access your wallet.")
async def wallet(interaction: discord.Interaction):
    await log_to_database(interaction.user.id, "/wallet")
    guild = interaction.guild
    # Check if the user is a member of the guild
    member = guild.get_member(interaction.user.id)
    if member:
        view = Wallet_exist()
        await interaction.response.send_message("Welcome to SideKick!\nClick on Wallet 🏦 to manage it.\nClick on Top Up 💵 to add funds.\nClick on Balance 📊 to view your USDT balance.", view=view, ephemeral=True)
        return
    else:
        await interaction.response.defer(ephemeral=True)
        try:
            # Create an invite that expires in 24 hours with a maximum of 10 uses
            invite = await guild.text_channels[0].create_invite(max_age=86400, max_uses=10, unique=True)
            await interaction.response.send_message(f"You must join our main guild to access your profile. Please join using this invite: {invite.url}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Failed to create an invite. Please check my permissions and try again.", ephemeral=True)
            print(e)


@bot.tree.command(name="points", description="Use this command to access your tasks.")
async def points(interaction: discord.Interaction):
    await log_to_database(interaction.user.id, "/tasks")
    await interaction.response.send_message("For available tasks press the link below:\nhttps://app.sidekick.fans/tasks", ephemeral=True)


@bot.tree.command(name="boost", description="Use this command to boost kickers!")
@app_commands.describe(username="The username to find.")
async def boost(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    view = BoostView(user_name=username)
    await view.initialize()
    await log_to_database(interaction.user.id, "/boost")
    if view.no_user:
        await interaction.followup.send(content="Sorry, there are no players.", ephemeral=True)
    else:
        await interaction.followup.send(embed=view.profile_embed, view=view, ephemeral=True)

@bot.event
async def on_ready():
    delete_old_channels.start()
    # bot.loop.create_task(delete_old_channels())
    # post_weekly_leaderboard.start()
    await bot.tree.sync()
    # await delete_all_threads_and_clear_csv()
    post_user_profiles.start()
    print(f'We have logged in as {bot.user}')

def run():
    bot.run(DISCORD_BOT_TOKEN)
