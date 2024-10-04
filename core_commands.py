import discord
from discord import app_commands
import discord.ext
import discord.ext.commands
import os

from views.play_view import PlayView
from bot_instance import get_bot
from background_tasks import delete_old_channels, post_user_profiles, create_leaderboard
from database.dto.sql_subscriber import Subscribers_Database
from database.dto.psql_services import Services_Database
from database.dto.sql_order import Order_Database
from config import (
    MAIN_GUILD_ID,
    DISCORD_BOT_TOKEN,
    ORDER_CATEGORY_NAME,
    ORDER_CHANNEL_NAME,
    LINK_LEADERBOARD,
)
from views.boost_view import BoostView
from views.exist_service import Profile_Exist
from views.wallet_view import Wallet_exist
from views.order_view import OrderView
from models.forum import get_or_create_forum
from models.thread_forum import start_posting
from models.public_channel import get_or_create_channel_by_category_and_name
from translate import get_lang_prefix, translations

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

async def save_user_id(user_id):
    services_db = Services_Database()
    existing_user_ids = await services_db.get_user_ids_wot_tournament()
    if user_id in existing_user_ids:
        return
    else:
        await services_db.save_user_wot_tournament(user_id)

@bot.tree.command(name="forum", description="Create or update SideKick forum! [Only channel owner]")
async def forum_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/forum", 
        interaction.guild.id if interaction.guild else None
    )

    guild: discord.guild.Guild = interaction.guild
    lang = get_lang_prefix(guild.id)
    try:
        forum_channel: discord.channel.ForumChannel = await get_or_create_forum(guild)
    except discord.DiscordException:
        await interaction.response.send_message(
            content=translations["not_community"][lang],
            ephemeral=True
        )
        return
    if not is_admin(interaction):
        await interaction.followup.send(
            content=translations["forum_no_permission"][lang],
            ephemeral=True
        )
        return
    await start_posting(forum_channel, guild, bot, order_type="ASC")
    await interaction.followup.send(
        content=translations["forum_posts_created"][lang],
        ephemeral=True
    )


@bot.tree.command(name="profile", description="Use this command if you wish to be part of the Sidekick Playmates network.")
async def profile(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/profile", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    profile_exist = Profile_Exist(str(interaction.user.id))
    lang = get_lang_prefix(interaction.guild.id)
    if profile_exist.no_user:
        await interaction.followup.send(
            translations["profile_not_created"][lang].format(link=os.getenv('WEB_APP_URL')),
            ephemeral=True
        )
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
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/go", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(interaction.guild.id)
    view = await PlayView.create(user_choice="ALL", lang=lang)

    if view.no_user:
        await interaction.followup.send(
            content=translations["no_players"][lang],
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            embed=view.profile_embed,
            view=view,
            ephemeral=True
        )


@bot.tree.command(name="find", description="Find a user profile by their username.")
@app_commands.describe(username="The username to find.")
async def find(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    view = await PlayView.create(username=username)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/find", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(interaction.guild.id)
    view = await PlayView.create(username=username, lang=lang)

    if view.no_user:
        await interaction.followup.send(
            content=translations["no_players"][lang],
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            embed=view.profile_embed,
            view=view,
            ephemeral=True
        )

async def get_guild_invite_link(guild_id):
    guild = bot.get_guild(guild_id)
    if guild:
        invite = "https://discord.gg/sidekick"  # Expires in 1 day, 1 use
        return invite
    return None

@bot.tree.command(name="order", description="Use this command to post your service request and summon Kickers to take the order.")
@app_commands.choices(choices=[app_commands.Choice(name="All players", value="ALL"),
                               app_commands.Choice(name="Casual", value="57c86488-8935-4a13-bae0-5ca8783e205d"),
                               app_commands.Choice(name="Coaching", value="88169d78-85b4-4fa3-8298-3df020f13a6f"),
                               app_commands.Choice(name="Just Chatting", value="2974b0e8-69de-4d7c-aa4d-d5aa8e05d360"),
                               app_commands.Choice(name="Watch Youtube", value="d3ae39d2-fd86-41d7-bc38-0b582ce338b5"),
                               app_commands.Choice(name="Play Games", value="79bf303a-318b-4815-bd56-7b0b49ae7bff"),
                               app_commands.Choice(name="Virtual Date", value="d6b9fc04-bfb2-46df-88eb-6e8c149e34d9"),
                               app_commands.Choice(name="World Of Tanks", value="2e851835-c033-4c90-a920-ffa75318235a")
                               ])
async def order(interaction: discord.Interaction, choices: app_commands.Choice[str]):
    guild_id = interaction.guild.id
    lang = get_lang_prefix(guild_id)
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/order", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    order_data = {
        'user_id': interaction.user.id,
        'task_id': choices.value
    }
    await Order_Database.set_user_data(order_data)
    main_link = await get_guild_invite_link(guild_id)
    channel = await get_or_create_channel_by_category_and_name(
        category_name=ORDER_CATEGORY_NAME,
        channel_name=ORDER_CHANNEL_NAME,
        guild=interaction.guild
    )
    text_message_order_view = \
        translations["order_new_alert"][lang].format(choice=choices.name)
    services_db = Services_Database(app_choice=choices.value)
    view = OrderView(customer=interaction.user, services_db=services_db, lang=lang)
    sent_message = await channel.send(
        view=view, content=f"@everyone\n{text_message_order_view}",
    )
    view.messages.append(sent_message)
    await interaction.followup.send(
        translations["order_dispatching"][lang].format(link=main_link),
        ephemeral=True
    )
    
    kicker_ids = await services_db.get_kickers_by_service_title(
        service_title=choices.name
    )
    for kicker_id in kicker_ids:
        try:
            kicker_id = int(kicker_id)
        except ValueError:
            print(f"ID: {kicker_id} is not int")
            continue
        kicker = bot.get_user(kicker_id)
        if not kicker:
            continue
        sent_message = await kicker.send(view=view, content=text_message_order_view)
        view.messages.append(sent_message)


@bot.tree.command(name="subscribe", description="Use this command to post your service request and summon Kickers to take the order.")
@app_commands.choices(choices=[app_commands.Choice(name="Subscribe", value=1),
                               app_commands.Choice(name="Unsubscribe", value=0),
                               ])
async def subscribe(interaction: discord.Interaction, choices: app_commands.Choice[int]):
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/subscribe", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    if choices.value == 1:
        await Subscribers_Database.set_user_data(interaction.user.id)
        await interaction.followup.send(f"You have successfully subscribed to the order command. Each time the /order command is used by users, you will receive a notification.", ephemeral=True)
    else:
        await Subscribers_Database.delete_user_data(interaction.user.id)
        await interaction.followup.send(f"You have unsubscribed from the order command.", ephemeral=True)


@bot.tree.command(name="wallet", description="Use this command to access your wallet.")
async def wallet(interaction: discord.Interaction):
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/wallet", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    main_guild = bot.get_guild(MAIN_GUILD_ID)
    lang = get_lang_prefix(interaction.guild.id)
    # Check if the user is a member of the guild
    member = main_guild.get_member(interaction.user.id)
    if member:
        view = Wallet_exist(lang=lang)
        await interaction.response.send_message(
            translations["wallet_message"][lang],
            view=view,
            ephemeral=True
        )
        return
    else:
        await interaction.response.defer(ephemeral=True)
        try:
            # Create an invite that expires in 24 hours with a maximum of 10 uses
            invite = await main_guild.text_channels[0].create_invite(max_age=86400, max_uses=10, unique=True)
            await interaction.response.send_message(
                translations["invite_join_guild"][lang].format(invite_url=invite.url),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                translations["failed_invite"][lang],
                ephemeral=True
            )
            print(e)


@bot.tree.command(name="points", description="Use this command to access your tasks.")
async def points(interaction: discord.Interaction):
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/tasks", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    await interaction.response.send_message(f"For available tasks press the link below:\n{os.getenv('WEB_APP_URL')}/tasks?side_auth=DISCORD", ephemeral=True)
    lang = get_lang_prefix(interaction.guild.id)
    link = os.getenv('WEB_APP_URL') + "/tasks?side_auth=DISCORD"
    await interaction.response.send_message(
        translations["points_message"][lang].format(link=link),
        ephemeral=True
    )


@bot.tree.command(name="boost", description="Use this command to boost kickers!")
@app_commands.describe(username="The username to find.")
async def boost(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/boost", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(interaction.guild.id)
    view = BoostView(user_name=username, lang=lang)
    await view.initialize()
    if view.no_user:
        await interaction.followup.send(
            content=translations["no_players"][lang],
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            embed=view.profile_embed,
            view=view,
            ephemeral=True
        )


@bot.tree.command(name="leaderboard", description="Check out the points leaderboard")
async def leaderboard(interaction: discord.Interaction):
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/leaderboard", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(interaction.guild.id)
    await interaction.response.send_message(
        embed=discord.Embed(
            color=discord.Colour.orange(),
            title=translations["leaderboard_title"][lang],
            description=translations["leaderboard"][lang],
            url=LINK_LEADERBOARD
        ),
        ephemeral=True
    )

# @bot.tree.command(name="wot_tournament", description="Register to WoT tournament")
# async def wot_tournament(interaction: discord.Interaction):
#     await Services_Database().log_to_database(
#         interaction.user.id, 
#         "/wot_tournament", 
#         interaction.guild.id if interaction.guild else None
#     )
#     services_db = Services_Database()
#     user_ids = await services_db.get_user_ids_wot_tournament()

#     if interaction.user.id in user_ids:
#         await interaction.response.send_message("Вы уже зарегистрировались.", ephemeral=True)
#         return
#     else:
#         await services_db.save_user_wot_tournament(interaction.user.id)
#         await interaction.response.send_message("Спасибо за регистрацию на турнире!", ephemeral=True)

@bot.event
async def on_ready():
    delete_old_channels.start()
    await bot.tree.sync()
    post_user_profiles.start()
    create_leaderboard.start()
    print(f'We have logged in as {bot.user}')

def run():
    bot.run(DISCORD_BOT_TOKEN)
