import discord

from bot_instance import get_bot
from config import BOOST_CHANNEL_ID, MAIN_GUILD_ID

from services.sqs_client import SQSClient
from views.access_reject import AccessRejectView
from views.check_reaction import CheckReactionView
from database.psql_services import Services_Database
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
    message_embend = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=f"Hey @{kicker.name}, @{customer.name} has purchased {service_name} session with you!!",
        description=(
            "Please click on accept, if you want to start a session with the user. "
            "In case you click on reject or do not respond within 15 minutes, "
            "the session will be canceled and funds will be refunded to the user."
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

    await customer.send(
        f"Dear {customer.name}, your purchase request has been sent to the kicker. A private voice room between two of you will be created once he/she accepts the order. \n"
        "In case the order has been rejected or left with no response for 15 minutes, the funds will be refunded to you."
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
