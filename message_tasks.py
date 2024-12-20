import asyncio
import random
from config import MESSAGES
import discord
from discord.ext import tasks
from database.dto.psql_services import Services_Database

from services.logger.client import CustomLogger
from views.buttons.stop_button import StopButton

logger = CustomLogger


async def choose_random_fact():
    services_db = Services_Database()
    facts = await services_db.get_facts()
    return random.choice(facts)


@tasks.loop(count=1)
async def send_scheduled_messages(channel):
    for delay, message, use_fact in MESSAGES:
        await asyncio.sleep(delay)
        try:
            if use_fact:
                message = await choose_random_fact()
                message = f"__Fun fact:__ \n{message}"
            await channel.send(message)
        except discord.HTTPException as e:
            await logger.error_discord(f"Failed to send message to channel {channel}: {e}")


@tasks.loop(count=1)
async def send_stop_button(channel):
    await asyncio.sleep(11)
    stop_button_view = StopButton(lambda: stop_all_messages(channel))
    await channel.send("**If the kicker has already joined the channel, please click on the \"Stop\" button to stop receiving notifications**", view=stop_button_view)


active_tasks = {}


async def handle_task(task, channel, action='start', task_name=None):
    task_key = f"{task_name}_{channel.name}"

    if active_tasks.get(task_key) and action == 'start':
        print(f"Task {task_name} is already running. Ignoring duplicate start.")
        return
    
    if task.is_running():
        print(f"Task {task_name} is already running. Stopping the task.")
        task.cancel()
        await asyncio.sleep(0.1)
    
    if action == 'start' and channel:
        task.start(channel)
        active_tasks[task_key] = task
        print(f"Task {task_name} started successfully.")
    elif action == 'stop':
        active_tasks.pop(task_key, None)
        print(f"Task {task_name} stopped successfully.")


async def start_all_messages(channel):
    await handle_task(send_scheduled_messages, channel, action='start', task_name='send_scheduled_messages')
    await handle_task(send_stop_button, channel, action='start', task_name='send_stop_button')


stop_lock = asyncio.Lock()


async def stop_all_messages(channel):
    async with stop_lock:
        await handle_task(send_scheduled_messages, channel, action='stop', task_name='send_scheduled_messages')
        await handle_task(send_stop_button, channel, action='stop', task_name='send_stop_button')
        return True