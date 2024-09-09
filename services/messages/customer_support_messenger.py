import discord
from config import CUSTOMER_SUPPORT_TEAM_IDS

async def send_message_to_customer_support(bot: discord.Client, message: str) -> None:
    for customer_support_id in CUSTOMER_SUPPORT_TEAM_IDS:
        try:
            customer_support = await bot.fetch_user(customer_support_id)
            await customer_support.send(message)
        except discord.HTTPException:
            print(f"Failed to send message to customer support with ID {customer_support_id}")
        except AttributeError:
            print(f"Failed to find user with ID {customer_support_id}")
