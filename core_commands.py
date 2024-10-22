import discord
from discord import app_commands
import discord.ext
import discord.ext.commands
import os
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
    GUIDE_CHANNEL_NAME
)
from views.boost_view import BoostView
from views.exist_service import Profile_Exist
from views.wallet_view import Wallet_exist
from views.order_view import OrderView
from models.forum import get_or_create_forum
from models.thread_forum import start_posting
from models.public_channel import get_or_create_channel_by_category_and_name
from models.enums import Genders, Languages
from translate import get_lang_prefix, translations

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
    view = await PlayView.create(user_choice="ALL")
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


@bot.tree.command(name="order", description="Use this command to post your service request and summon Kickers to take the order.")
@app_commands.choices(choices=[
    app_commands.Choice(name="All players", value="ALL"),
    app_commands.Choice(name="Casual", value="57c86488-8935-4a13-bae0-5ca8783e205d"),
    app_commands.Choice(name="Coaching", value="88169d78-85b4-4fa3-8298-3df020f13a6f"),
    app_commands.Choice(name="Just Chatting", value="2974b0e8-69de-4d7c-aa4d-d5aa8e05d360"),
    app_commands.Choice(name="Watch Youtube", value="d3ae39d2-fd86-41d7-bc38-0b582ce338b5"),
    app_commands.Choice(name="Play Games", value="79bf303a-318b-4815-bd56-7b0b49ae7bff"),
    app_commands.Choice(name="Virtual Date", value="d6b9fc04-bfb2-46df-88eb-6e8c149e34d9"),
    app_commands.Choice(name="World Of Tanks", value="2e851835-c033-4c90-a920-ffa75318235a")
])
@app_commands.choices(gender=[
    app_commands.Choice(name="Female", value=Genders.FEMALE.value),
    app_commands.Choice(name="Male", value=Genders.MALE.value),
    app_commands.Choice(name="Unimportant", value=Genders.UNIMPORTANT.value),
])
@app_commands.choices(language=[
    app_commands.Choice(name="Russian", value=Languages.RU.value),
    app_commands.Choice(name="English", value=Languages.EN.value),
    app_commands.Choice(name="Spanish", value=Languages.ES.value),
    app_commands.Choice(name="French", value=Languages.FR.value),
    app_commands.Choice(name="German", value=Languages.DE.value),
    app_commands.Choice(name="Italian", value=Languages.IT.value),
    app_commands.Choice(name="Portuguese", value=Languages.PT.value),
    app_commands.Choice(name="Chinese", value=Languages.ZH.value),
    app_commands.Choice(name="Japanese", value=Languages.JA.value),
    app_commands.Choice(name="Korean", value=Languages.KO.value),
    app_commands.Choice(name="Arabic", value=Languages.AR.value),
    app_commands.Choice(name="Hindi", value=Languages.HI.value),
    app_commands.Choice(name="Turkish", value=Languages.TR.value),
    app_commands.Choice(name="Persian", value=Languages.FA.value),
    app_commands.Choice(name="Unimportant", value=Languages.UNIMPORTANT.value),
])
@app_commands.describe(text='Order description')
async def order(
    interaction: discord.Interaction,
    choices: app_commands.Choice[str],
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
        'task_id': choices.value
    }
    await Order_Database.set_user_data(order_data)
    main_link = await get_guild_invite_link(guild_id)
    services_db = Services_Database(
        app_choice=choices.value,
        sex_choice=gender.value,
        language_choice=language.value
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
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/wallet", 
        guild_id
    )
    await save_user_id(interaction.user.id)
    main_guild = bot.get_guild(MAIN_GUILD_ID)
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
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
    guild_id: int = interaction.guild_id if interaction.guild_id else None
    await Services_Database().log_to_database(
        interaction.user.id, 
        "/tasks", 
        guild_id
    )
    await save_user_id(interaction.user.id)
    await interaction.response.send_message(f"For available tasks press the link below:\n{os.getenv('WEB_APP_URL')}/tasks?side_auth=DISCORD", ephemeral=True)
    lang = get_lang_prefix(guild_id)
    if not guild_id:
        await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
        return
    link = os.getenv('WEB_APP_URL') + "/tasks?side_auth=DISCORD"
    await interaction.response.send_message(
        translations["points_message"][lang].format(link=link),
        ephemeral=True
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


@bot.event
async def on_guild_join(guild: discord.Guild):
    message: str = translations["en"]["bot_guild_join_message"].format(server_name=guild.name)
    image = await ImageS3Bucket.get_image_by_url(
        "https://discord-photos.s3.eu-central-1.amazonaws.com/sidekick-back-media/discord_bot/initial_server.png"
    )
    channel = await get_or_create_channel_by_category_and_name(
        category_name=GUIDE_CATEGORY_NAME,
        channel_name=GUIDE_CHANNEL_NAME,
        guild=guild
    )
    try:
        await channel.send(message, file=discord.File(image))
    except discord.DiscordException as e:
        logger.error(str(e))


@bot.event
async def on_ready():
    delete_old_channels.start()
    await bot.tree.sync()
    post_user_profiles.start()
    create_leaderboard.start()
    send_random_guide_message.start()
    print(f'We have logged in as {bot.user}')

def run():
    bot.run(DISCORD_BOT_TOKEN)
