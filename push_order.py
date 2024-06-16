import asyncio
import time
from bot_instance import get_bot
from sql_profile import Profile_Database
from sql_order import Order_Database
import random
from getServices import DiscordServiceFetcher

from message_constructors import create_profile_embed
from button_constructors import AcceptView, ButtonAcceptView
from config import TASK_DESCRIPTIONS, MAIN_GUILD_ID
bot = get_bot()


async def get_guild_invite_link(guild_id):
    guild = bot.get_guild(guild_id)
    if guild:
        # Create an invite link
        invite = "https://discord.gg/sidekick"  # Expires in 1 day, 1 use
        return invite
    return None

async def send_push_notifications(order_id):
    order_data = await Order_Database.get_order_data(order_id)
    task_id = order_data.get("task_id")
    # all_user_ids = await Profile_Database.get_user_ids_by_task_id(task_id)
    userData = DiscordServiceFetcher(serviceTypeId=task_id)
    userData.fetch_services()
    # Get all user IDs from Profile_Database
    # all_user_ids = await Profile_Database.get_all_user_ids()

    # Get the pushed user IDs for the given order_id
    pushed_user_ids = await Order_Database.get_pushed_user_ids(order_id)

    # Filter out users who have already been pushed
    # users_to_push = [user_id for user_id in all_user_ids if user_id not in pushed_user_ids]

    # users_to_push = ['930005621728763904', '689328299247534080', '676632838455427092']

    # Limit to 20 users
    # users_to_push = random.sample(users_to_push, min(20, len(users_to_push)))

    # Send push notifications
    tasks = []

    for _ in range(20):  # Loop 20 times
        time.sleep(1)
        current_user = userData.get_next()
        if current_user:  # Check if get_next() returns a valid user
            discord_id = current_user["discordId"]
            tasks.append(process_user_push(order_id, discord_id, current_user))

    await asyncio.gather(*tasks)
    # tasks = [process_user_push(order_id, user_id) for user_id in users_to_push]
    # await asyncio.gather(*tasks)

async def process_user_push(order_id, user_id, current_user):
    try:
        await asyncio.sleep(1)
        user = await bot.fetch_user(user_id)
        if user:
            order_data = await Order_Database.get_order_data(order_id)
            customer_user_id = order_data.get("user_id")
            task_id = order_data.get("task_id")

            # customer_data = await Profile_Database.get_user_data(user_id)
            button = ButtonAcceptView(customer_user_id, task_id, order_id, current_user)

            task_desc = TASK_DESCRIPTIONS[task_id]

            # print("CUSTOMER NAME: ", customer_data["name"])
            # customer_language = customer_data.get("language", "N/A")
            # customer_language = "EN"
            main_link = await get_guild_invite_link(MAIN_GUILD_ID)

            await user.send(content=f"New Order Summon Alert: {task_desc}.\n You have a new order summon for a {task_desc}.\nAccept to send your profile to the user.\nPlease ensure to join our server using the link below: {main_link}", view=button)

            await Order_Database.insert_push_order(order_id, user_id)
            # Update push_count
            push_count = await update_push_count(order_id)

            # If push_count exceeds 100, set status to 1
            if push_count > 40:
                await Order_Database.update_column(order_id, 'status', 0)

    except Exception as e:
        print(f"Failed to send message to user {user_id}: {e}")

async def update_push_count(order_id):
    # Fetch the current push_count
    order_data = await Order_Database.get_order_data(order_id)
    push_count = order_data['push_count'] + 1

    # Update the push_count in the database
    await Order_Database.update_column(order_id, 'push_count', push_count)
    return push_count

async def iterative_push_notifications():
    while True:
        await asyncio.sleep(15)
        # Get all active order IDs
        active_order_ids = await Order_Database.get_active_order_ids()
        # Send push notifications for each active order ID
        for order_id in active_order_ids:
            # print(f"The order to be checked: {order_id}")
            await send_push_notifications(order_id)

def start_push_notifications():
    future = asyncio.run_coroutine_threadsafe(iterative_push_notifications(), bot.loop)
    try:
        future.result()  # Wait for the coroutine to finish
    except Exception as e:
        print(f"Error running push notifications: {e}")

if __name__ == "__main__":
    start_push_notifications()
