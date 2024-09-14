from typing import Union
import discord
from discord import app_commands
import discord.ext
import discord.ext.commands
from play_view import PlayView
from bot_instance import get_bot
from background_tasks import delete_old_channels, post_user_profiles
from database.dto.sql_subscriber import Subscribers_Database
from database.dto.sql_profile import log_to_database
from database.dto.psql_services import Services_Database

from models.forum import get_or_create_forum
import os

from config import MAIN_GUILD_ID, DISCORD_BOT_TOKEN, ORDER_CHANNEL_ID
from database.dto.sql_order import Order_Database
from services.messages.base import send_confirm_order_message
from views.boost_view import BoostView
from views.exist_service import Profile_Exist
from views.wallet_view import Wallet_exist
from views.order_view import OrderView

main_guild_id = MAIN_GUILD_ID
bot = get_bot()

##### To get list of users who are currently online #####
async def list_online_users(guild):
    if guild is None:
        return []
    online_members = [member for member in guild.members if str(member.status) == 'online']
    online_member_ids = [member.id for member in online_members]
    return online_member_ids


def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.guild is not None and interaction.guild.owner_id == interaction.user.id


def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator


@bot.tree.command(name="forum", description="Create or update SideKick forum! [Only channel owner]")
async def forum_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild: discord.guild.Guild = interaction.guild
    try:
        forum_channel: discord.channel.ForumChannel = await get_or_create_forum(guild)
    except discord.DiscordException:
        await interaction.response.send_message(content="Discord channel is not community!", ephemeral=True)
        return
    if not is_admin(interaction):
        await interaction.followup.send(content='Oops, you do not have right to use this command!', ephemeral=True)
        return
    services_db = Services_Database(order_type="ASC")
    await services_db.start_posting(forum_channel, guild, bot)
    await interaction.followup.send(content="Posts created!", ephemeral=True)


@bot.tree.command(name="profile", description="Use this command if you wish to be part of the Sidekick Playmates network.")
async def profile(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await log_to_database(interaction.user.id, "/profile")
    profile_exist = Profile_Exist(str(interaction.user.id))
    await profile_exist.initialize()
    if profile_exist.no_user:
        await interaction.followup.send(f"Looks like you haven't created a profile with us! Please click the link below to create your profile.\n{os.getenv('WEB_APP_URL')}/profile", ephemeral=True)
    else:
        await interaction.followup.send(embed=profile_exist.profile_embed, view=profile_exist, ephemeral=True)


async def list_all_users_with_online_status(guild):
    if guild is None:
        return []
    all_member_ids = [member.id for member in guild.members]
    return all_member_ids


@bot.tree.command(name="go", description="Use this command and start looking for playmates!")
async def play(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    view = await PlayView.create(user_choice="ALL")
    await log_to_database(interaction.user.id, "/go")

    if view.no_user:
        await interaction.followup.send(content="Sorry, there are no players.", ephemeral=True)
    else:
        await interaction.followup.send(embed=view.profile_embed, view=view, ephemeral=True)


@bot.tree.command(name="find", description="Find a user profile by their username.")
@app_commands.describe(username="The username to find.")
async def find(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    view = await PlayView.create(user_choice="ALL", username=username)
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
    channel = bot.get_channel(ORDER_CHANNEL_ID)
    view = OrderView(customer=interaction.user, user_choises=choices.value)
    view.message = await channel.send(
        view=view,
        content=(
            "@everyone \n"
            f"New Order Alert: **{choices.name}** [30 minutes]\n"
            f"You have a new order for a **{choices.name}** in english"
        )
    )
    await interaction.followup.send(f"Your order is dispatching now. Once there are Kickers accepting the order, their profile will be sent to you via DM.\n{main_link}", ephemeral=True)


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
    await interaction.response.send_message(f"For available tasks press the link below:\n{os.getenv('WEB_APP_URL')}/tasks", ephemeral=True)


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
