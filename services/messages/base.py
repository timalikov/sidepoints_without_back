import discord

from bot_instance import get_bot
from config import BOOST_CHANNEL_ID, MAIN_GUILD_ID

from services.messages.customer_support_messenger import send_message_to_customer_support
from services.sqs_client import SQSClient
from views.access_reject import AccessRejectView
from views.check_reaction import CheckReactionView
from database.dto.psql_services import Services_Database
from models.enums import StatusCodes
from models.public_channel import find_channel_by_category_and_name

bot = get_bot()


async def send_kickers_reaction_test() -> StatusCodes:
    service = Services_Database()
    kickers = await service.get_kickers()
    for kicker_id in kickers:
        kicker: discord.User = bot.get_user(kicker_id)
        btn = CheckReactionView(kicker=kicker)
        await kicker.send(
            (
                f"Hi {kicker.name}, we’re "
                "doing a quick check to see "
                "if you're available online. "
                "Please click the 'Check' button "
                "below within the next 5 minutes "
                "to pass the test.!"
            ),
            view=btn
        )
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
    channel_name: str,
    customer: discord.User,
    kicker: discord.User,
    kicker_username: str,
    service_name: str = "",
    purchase_id: int
) -> StatusCodes:
    services_db = Services_Database()
    service = await services_db.get_services_by_username(username=kicker_username)
    if service:
        service["service_category_name"] = await services_db.get_service_category_name(service["service_type_id"])

    
    cs_team_message = (
        "**Session has been purchased**\n"
        f"User: <@{customer.id}>\n"
        f"Kicker: <@{kicker.id}>\n"
        # f"Service: {service["service_category_name"]}\n"
        # f"Price: {service["service_price"]}\n"
    )
    await send_message_to_customer_support(bot, cs_team_message)

    await customer.send(
        f"Your order has been sent to kicker <@{kicker.id}>.\n"
        "If there is no response within 1 minute, you will be able to replace the kicker, or refund the money."
    )

    message_embend = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=f"Your service has been purchased:",
        description=(
            f"Service: {service["service_category_name"] if service else "Not found"}\n" 
            # f"Price: {service['service_price']}\n"
            "Please accept or reject the session"
        )       
    )
    
    sqs_client = SQSClient()

    view = AccessRejectView(
        kicker=kicker,
        customer=customer,
        kicker_username=kicker_username,
        channel_name=channel_name,
        service_name=service_name,
        purchase_id=purchase_id,
        sqs_client=sqs_client
    )

    try:
        view.message = await kicker.send(
            view=view,
            embed=message_embend
        )
        return True, view.message.channel.id
    except Exception as e:
        return False, f"Failed to send message: {str(e)}"


async def send_reaction_message() -> StatusCodes:
    ...
