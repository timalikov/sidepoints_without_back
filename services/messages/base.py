import discord

from bot_instance import get_bot

from views.access_reject import AccessRejectView
from models.enums import StatusCodes

bot = get_bot()


async def send_discord_notification(*, user_id: int, message: str) -> int:
    try:
        user: discord.User = await bot.fetch_user(int(user_id))
    except (ValueError, discord.NotFound):
        return False
    _: discord.Message = await user.send(message)
    return True


async def send_confirm_order_message(
    *,
    channel_name: str,
    customer: discord.User,
    kicker: discord.User,
    kicker_username: str,
    service_name: str = ""
) -> StatusCodes:
    message_embend = discord.Embed(
        colour=discord.Colour.dark_blue(),
        title=f"Hey @{kicker.name} you'r service {service_name} has been purchased!",
        description=(
            "Do you want to accept the session ? "
            "If yes, click on accept button and DM "
            "the user to get the session started! "
            "Once the session is delivered, "
            "the funds will be transfered to you!" 
        )       
    )
    view = AccessRejectView(
        kicker=kicker,
        customer=customer,
        kicker_username=kicker_username,
        channel_name=channel_name,
        service_name=service_name
    )
    await kicker.send(
        view=view,
        embed=message_embend
    )
