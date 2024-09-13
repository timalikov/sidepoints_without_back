from datetime import datetime
from button_constructors import InformKickerButton
import discord
from config import CUSTOMER_SUPPORT_TEAM_IDS, TEAM_CHANNEL_ID

async def send_message_to_customer_support(bot: discord.Client, message: str) -> None:
    for customer_support_id in CUSTOMER_SUPPORT_TEAM_IDS:
        try:
            customer_support = await bot.fetch_user(customer_support_id)
            await customer_support.send(message)
        except discord.HTTPException:
            print(f"Failed to send message to customer support with ID {customer_support_id}")
        except AttributeError:
            print(f"Failed to find user with ID {customer_support_id}")

    return

async def send_message_to_team_channel(*, bot: discord.Client, customer: discord.User, kicker: discord.User, invite_url: str) -> None:
    message = (
        f"Customer: <@{customer.id}> {customer.name}\n"
        f"Kicker: <@{kicker.id}> {kicker.name}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Link: {invite_url} "
    )
    channel = bot.get_channel(TEAM_CHANNEL_ID)
    
    if channel is not None:
        view = InformKickerButton(kicker)
        await channel.send(content=message, view=view)
    else:
        print(f"Channel with ID {TEAM_CHANNEL_ID} not found.")

    return