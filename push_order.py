import asyncio
import random

from config import TASK_DESCRIPTIONS, MAIN_GUILD_ID
from bot_instance import get_bot

from database.dto.sql_order import Order_Database
from database.dto.sql_subscriber import Subscribers_Database
from services.utils import get_guild_invite_link
from services.logger.client import CustomLogger
from views.button_accept_view import ButtonAcceptView

logger = CustomLogger
bot = get_bot()


async def send_push_notifications(order_id):
    order_data = await Order_Database.get_order_data(order_id)
    all_user_ids = await Subscribers_Database.get_all_discord_ids()
    pushed_user_ids = await Order_Database.get_pushed_user_ids(order_id)
    users_to_push = [user_id for user_id in all_user_ids if user_id not in pushed_user_ids]

    # Limit to 20 users
    users_to_push = random.sample(users_to_push, min(20, len(users_to_push)))

    # Send push notifications
    tasks = [process_user_push(order_id, user_id) for user_id in users_to_push]
    await asyncio.gather(*tasks)

async def process_user_push(order_id, user_id):
    try:
        await asyncio.sleep(1)
        user = await bot.fetch_user(user_id)
        if user:
            order_data = await Order_Database.get_order_data(order_id)
            customer_user_id = order_data.get("user_id")
            task_id = order_data.get("task_id")
            button = ButtonAcceptView(customer_user_id, task_id, order_id, user)
            task_desc = TASK_DESCRIPTIONS[task_id]
            main_link = await get_guild_invite_link(MAIN_GUILD_ID)
            await user.send(
                content=f"New Order Summon Alert: {task_desc}.\n You have a new order summon for a {task_desc}.\nAccept to send your profile to the user.\nPlease ensure to join our server using the link below: {main_link}",
                view=button
            )
            await Order_Database.insert_push_order(order_id, user_id)

            # Update push_count
            push_count = await update_push_count(order_id)

            # If push_count exceeds 100, set status to 1
            if push_count > 40:
                await Order_Database.update_column(order_id, 'status', 0)

    except Exception as e:
        await logger.error_discord(f"Failed to send message to user {user_id}: {e}")

async def update_push_count(order_id):
    # Fetch the current push_count
    order_data = await Order_Database.get_order_data(order_id)
    push_count = order_data['push_count'] + 1

    # Update the push_count in the database
    await Order_Database.update_column(order_id, 'push_count', push_count)
    return push_count

async def iterative_push_notifications():
    while True:
        # Get all active order IDs
        active_order_ids = await Order_Database.get_active_order_ids()
        # Send push notifications for each active order ID
        for order_id in active_order_ids:
            await send_push_notifications(order_id)

def start_push_notifications():
    future = asyncio.run_coroutine_threadsafe(iterative_push_notifications(), bot.loop)
    try:
        future.result()  # Wait for the coroutine to finish
    except Exception as e:
        print(f"Error running push notifications: {e}")

if __name__ == "__main__":
    start_push_notifications()
