import asyncio
import uuid
import discord

from bot_instance import get_bot
from config import BOOST_CHANNEL_ID, MAIN_GUILD_ID, TEST_ACCOUNTS
from translate import translations, get_lang_prefix

from services.messages.customer_support_messenger import send_message_to_customer_support
from services.sqs_client import SQSClient
from views.access_reject import AccessRejectView
from views.check_reaction import CheckReactionView
from views.order_view import OrderView
from database.dto.psql_services import Services_Database
from models.enums import StatusCodes
from models.public_channel import find_channel_by_category_and_name

bot = get_bot()


async def send_kickers_reaction_test() -> StatusCodes:
    service = Services_Database()
    kickers = await service.get_kickers()
    for kicker_id in kickers:
        kicker: discord.User = bot.get_user(kicker_id)
        btn = CheckReactionView(kicker=kicker, lang="en")
        message = translations["kicker_reaction_test_message"][btn.lang].format(kicker_name=kicker.name)
        await kicker.send(message, view=btn)
    return StatusCodes.SUCCESS

async def send_boost_message(*, image_url: str, message: str) -> StatusCodes:
    guild = bot.get_guild(MAIN_GUILD_ID)
    channel = guild.get_channel(BOOST_CHANNEL_ID)
    if not channel:
        channel = await find_channel_by_category_and_name(
            category_name="community",
            channel_name="🚀general"
        )
    if not channel:
        return StatusCodes.BAD, "Channel not found"
    try:
        await channel.send(
            embed=discord.Embed().set_image(url=image_url),
            content=f"@everyone {message}"
        )
    except discord.DiscordException:
        return StatusCodes.BAD, "Bot do not have right to send message!"
    return StatusCodes.SUCCESS, "ok"

async def send_discord_notification(*, user_id: int, message: str) -> bool:
    try:
        user: discord.User = await bot.fetch_user(int(user_id))
        _: discord.Message = await user.send(message)
    except (ValueError, discord.NotFound, discord.errors.Forbidden):
        return False
    return True

async def send_confirm_order_message(
    *,
    customer: discord.User,
    kicker: discord.User,
    kicker_username: str,
    purchase_id: int,
    discord_server_id: int,
    service_name: str = "",
) -> StatusCodes:
    lang = get_lang_prefix(int(discord_server_id))
    services_db = Services_Database()
    service = await services_db.get_services_by_username(username=kicker_username)
    if service:
        service["service_category_name"] = service["tag"]

    cs_team_message = translations["session_purchased"][lang].format(
        customer_name=customer.name,
        kicker_name=kicker.name,
        service_name=service['service_category_name'] if service else 'Not found',
        service_price=service['service_price'] if service else 'Not found'
    )
    
    if kicker.id not in TEST_ACCOUNTS and customer.id not in TEST_ACCOUNTS:
        await send_message_to_customer_support(bot, cs_team_message)

    await customer.send(
        translations["order_sent"][lang].format(kicker_name=kicker.name)
    )

    message_embend = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=translations["service_purchased_title"][lang],
        description=translations["service_details"][lang].format(
            service_name=service['service_category_name'] if service else 'Not found',
            service_price=service['service_price'] if service else 'Not found'
        )       
    )
    
    sqs_client = SQSClient()

    view = AccessRejectView(
        kicker=kicker,
        customer=customer,
        kicker_username=kicker_username,
        service_name=service_name,
        purchase_id=purchase_id,
        sqs_client=sqs_client,
        discord_server_id=discord_server_id,
        lang=lang
    )

    success: bool = True
    response: str = None
    try:
        view.message = await kicker.send(
            view=view,
            embed=message_embend
        )
    except Exception as e:
        response = translations["failed_to_send_message"][lang].format(error=str(e))
        success = False
    if view.message.channel:
        response = view.message.channel.id
    else:
        response = "Direct message"
    return success, response

async def send_reaction_message() -> StatusCodes:
    ...


async def send_order_message(
    order_id: uuid.UUID,
    language: str,
    gender: str,
    tag_name: str = "ALL",
    extra_text: str = ""
) -> StatusCodes:
    dto = Services_Database(
        app_choice=tag_name if tag_name else None,
        language_choice=language,
        sex_choice=gender
    )
    view = OrderView(
        customer=None,
        guild_id=MAIN_GUILD_ID,
        services_db=dto,
        order_id=order_id,
        extra_text=extra_text
    )
    await view.send_kickers_message()
    return True