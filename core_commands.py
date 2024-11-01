from database.dto.psql_leaderboard import LeaderboardDatabase
import os
import discord
from discord import app_commands
import discord.ext
import discord.ext.commands
from logging import getLogger

from services.messages.interaction import send_interaction_message
from services.storage.bucket import ImageS3Bucket
from views.play_view import PlayView
from bot_instance import get_bot
from background_tasks import (
    delete_old_channels,
    post_user_profiles,
    create_leaderboard,
    send_random_guide_message
)
from database.dto.sql_subscriber import Subscribers_Database
from database.dto.psql_services import Services_Database
from database.dto.sql_order import Order_Database
from config import (
    MAIN_GUILD_ID,
    DISCORD_BOT_TOKEN,
    LINK_LEADERBOARD,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME,
    TEST
)
from views.boost_view import BoostView
from views.exist_service import Profile_Exist
from views.points_view import PointsView
from views.order_view import OrderView
from views.top_up_view import TopUpDropdownMenu
from models.forum import get_or_create_forum
from models.thread_forum import start_posting
from models.public_channel import get_or_create_channel_by_category_and_name
from models.payment import (
    get_server_wallet_by_discord_id
)
from web3_interaction.balance_checker import get_usdt_balance
from translate import get_lang_prefix, translations
from services.cogs.invite_tracker import InviteTracker  
from core_command_choices import (
    servers_autocomplete,
    services_autocomplete,
    language_options,
    gender_options
)

main_guild_id: int = MAIN_GUILD_ID
bot = get_bot()
logger = getLogger("")

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
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/forum", 
        guild_id
    )
    guild: discord.guild.Guild = interaction.guild
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
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
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/profile", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
    profile_exist = Profile_Exist(discord_id=interaction.user.id, lang=lang)
    await profile_exist.initialize()
    if profile_exist.no_user:
        await send_interaction_message(interaction=interaction, message=translations["profile_not_created"][lang].format(link=os.getenv('WEB_APP_URL')))
    elif profile_exist.no_service:
        await send_interaction_message(interaction=interaction, message=translations["profile_no_service"][lang].format(link=os.getenv('WEB_APP_URL')))
    else:
        await interaction.followup.send(embed=profile_exist.profile_embed, view=profile_exist, ephemeral=True)


async def list_all_users_with_online_status(guild):
    if guild is None:
        return []
    all_member_ids = [member.id for member in guild.members]
    return all_member_ids


@bot.tree.command(name="start", description="Use this command and start looking for playmates!")
async def play(interaction: discord.Interaction):
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/go", 
        guild_id
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
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
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await interaction.response.defer(ephemeral=True)
    view = await PlayView.create(username=username)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/find", 
        guild_id
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
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


@bot.tree.command(name="go", description="Use this command to post your service request and summon ALL Kickers to take the order.")
async def order_all(interaction: discord.Interaction):
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/order", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(interaction.user.id)
    order_data = {
        'user_id': interaction.user.id,
        'task_id': "ALL"
    }
    await Order_Database.set_user_data(order_data)
    main_link = await get_guild_invite_link(guild_id)
    services_db = Services_Database(app_choice="ALL")
    view = OrderView(
        customer=interaction.user,
        services_db=services_db,
        lang=lang,
        guild_id=guild_id
    )
    await interaction.followup.send(
        translations["order_dispatching"][lang].format(link=main_link),
        ephemeral=True
    )
    await view.send_all_messages()


@bot.tree.command(
    name="order",
    description="Use this command to post your service request and summon Kickers to take the order."
)
@app_commands.autocomplete(choices=services_autocomplete)
@app_commands.autocomplete(server=servers_autocomplete)
@app_commands.choices(gender=gender_options)
@app_commands.choices(language=language_options)
@app_commands.describe(text='Order description')
async def order(
    interaction: discord.Interaction,
    choices: str,
    server: str,
    gender: app_commands.Choice[str],
    language: app_commands.Choice[str],
    text: str = ""
):
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/order", 
        guild_id
    )
    await save_user_id(interaction.user.id)
    order_data = {
        'user_id': interaction.user.id,
        'task_id': choices
    }
    await Order_Database.set_user_data(order_data)
    main_link = await get_guild_invite_link(guild_id)
    services_db = Services_Database(
        app_choice=choices,
        sex_choice=gender.value,
        language_choice=language.value,
        server_choice=(
            server 
            if server.lower() != "all servers" 
            and server.lower() != "no available servers"
            else None
        )
    )
    view = OrderView(
        customer=interaction.user,
        services_db=services_db,
        lang=lang,
        guild_id=guild_id,
        extra_text=text
    )
    await interaction.followup.send(
        translations["order_dispatching"][lang].format(link=main_link),
        ephemeral=True
    )
    await view.send_all_messages()


@bot.tree.command(name="subscribe", description="Use this command to post your service request and summon Kickers to take the order.")
@app_commands.choices(choices=[app_commands.Choice(name="Subscribe", value=1),
                               app_commands.Choice(name="Unsubscribe", value=0),
                               ])
async def subscribe(interaction: discord.Interaction, choices: app_commands.Choice[int]):
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/subscribe", 
        guild_id
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
    await interaction.response.defer(ephemeral=True)
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    lang = get_lang_prefix(guild_id)
    wallet: str = await get_server_wallet_by_discord_id(user_id=interaction.user.id)
    balance: int = get_usdt_balance(wallet) if wallet else 0
    message: str = translations["wallet_balance_message"][lang].format(
        balance=balance, wallet=wallet
    )
    dropdown = TopUpDropdownMenu(lang=lang)
    view = discord.ui.View(timeout=None)
    view.add_item(dropdown)
    await send_interaction_message(
        interaction=interaction,
        embed=discord.Embed(
            description=message,
            title=translations["wallet_title"][lang],
            colour=discord.Colour.orange()
        ),
        view=view
    )

@bot.tree.command(name="boost", description="Use this command to boost kickers!")
@app_commands.describe(username="The username to find.")
async def boost(interaction: discord.Interaction, username: str):
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await interaction.response.defer(ephemeral=True)
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/boost", 
        guild_id
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
    view = BoostView(user_name=username, lang=lang)
    await view.initialize()
    if view.no_user:
        if interaction.response.is_done():
            await interaction.followup.send(
                content=translations["no_players"][lang],
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                content=translations["no_players"][lang],
                ephemeral=True
            )

    else:
        if interaction.response.is_done():
            await interaction.followup.send(
                embed=view.profile_embed,
                view=view,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=view.profile_embed,
                view=view,
                ephemeral=True
            )


@bot.tree.command(name="leaderboard", description="Check out the points leaderboard")
async def leaderboard(interaction: discord.Interaction):
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/leaderboard", 
        guild_id
    )
    await save_user_id(interaction.user.id)
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
    await interaction.response.send_message(
        embed=discord.Embed(
            color=discord.Colour.orange(),
            title=translations["leaderboard_title"][lang],
            description=translations["leaderboard"][lang],
            url=LINK_LEADERBOARD
        ),
        ephemeral=True
    )

@bot.tree.command(name="points", description="See your points and tasks")
async def points(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    
    user_id = interaction.user.id
    services_db = Services_Database()
    await services_db.log_to_database(
        user_id, 
        "/points", 
        interaction.guild.id if interaction.guild else None
    )
    await save_user_id(user_id)
    guild_id = interaction.guild_id if interaction.guild_id else None
    lang = get_lang_prefix(guild_id)

    username = interaction.user.name
    profile_id = await services_db.get_user_profile_id(discord_id=user_id)
    if not profile_id:
        await send_interaction_message(interaction=interaction, message=translations["profile_not_found"][lang])
        return

    dto = LeaderboardDatabase()
    user_ranking = await dto.get_user_ranking(profile_id=profile_id)
    
    total_points = user_ranking.get('total_score', 0) if user_ranking else 0
    rank = user_ranking.get('total_pos', 0) if user_ranking else 0

    view = PointsView(
        username=username,
        total_points=total_points, 
        rank=rank, 
        lang=lang
    )

    send_method = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
    await send_method(embed=view.embed_message, view=view)


@bot.event
async def on_guild_join(guild: discord.Guild):
    message: str = "@everyone\n" + translations["welcome_message"]["en"].format(server_name=guild.name)
    image = await ImageS3Bucket.get_image_by_url(
        "https://discord-photos.s3.eu-central-1.amazonaws.com/sidekick-back-media/discord_bot/%3AHow+to+make+an+order.png"
    )
    channel = await get_or_create_channel_by_category_and_name(
        category_name=GUIDE_CATEGORY_NAME,
        channel_name=GUIDE_CHANNEL_NAME,
        guild=guild
    )
    try:
        await channel.send(message, file=discord.File(image, "guild_join.png"))
    except discord.DiscordException as e:
        logger.error(str(e))


@bot.event
async def on_ready():
    delete_old_channels.start()
    await bot.add_cog(InviteTracker(bot))
    await bot.tree.sync()
    post_user_profiles.start()
    create_leaderboard.start()
    # send_random_guide_message.start()
    print(f"We have logged in as {bot.user}. Is test: {'Yes' if TEST else 'No'}. Bot: {bot}")


def run():
    bot.run(DISCORD_BOT_TOKEN)
