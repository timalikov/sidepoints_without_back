import asyncio
import random
from button_constructors import StopButton
import discord
from discord.ext import tasks
from database.psql_services import Services_Database


async def choose_random_fact():
    services_db = Services_Database()
    facts = await services_db.get_facts()
    return random.choice(facts)

messages = [
    (10, "🚀 Just a quick update: We're on it! Thanks for your patience! 🌟 Kicker should join within 5 minutes, otherwise we will refund your money.", False),
    (20, "🔧 Our team is working their magic! Hang tight - we're almost there! Kicker should join within 4 minutes 40 seconds, otherwise we will refund your money.", False),
    (40, "⏳ Thanks for sticking with us! We’re making progress, stay tuned! 🚀 Kicker should join within 4 minutes 20 seconds, otherwise we will refund your money.", False),
    (60, "", True), 
    (80, "💪 We’re on a mission to get this sorted for you! Thanks for your patience! 🙌 Kicker should join within 3 minutes 40 seconds, otherwise we will refund your money.", False),
    (110, "🛠️ Almost there! Our team is busy behind the scenes. We appreciate your patience! 🎉 Kicker should join within 3 minutes 10 seconds, otherwise we will refund your money.", False),
    (150, "🎯 We’re making strides! Thanks for hanging in there – we’ll be with you shortly! 🚀 Kicker should join within 2 minutes 30 seconds, otherwise we will refund your money.", False),
    (180, "", True),
    (210, "✨ Just a little bit more time! We’re working hard to get everything sorted. Thanks! 💪 Kicker should join within 1 minute 30 seconds, otherwise we will refund your money.", False),
    (240, "🔍 Almost ready! Our team is doing their thing. Thanks for waiting! 🙌 Kicker should join within 1 minute, otherwise we will refund your money.", False),
    (255, "Oops! Looks like we hit a snag. We're on it and will make it right soon! 🙌 Kicker should join within 45 seconds, otherwise we will refund your money.", False),
    (270, "Oops! 😬 We hit a snag and couldn’t deliver. No worries – get your refund 💸 <#1233350206280437760>. Thanks for your patience! Kicker should join within 30 seconds, otherwise we will refund your money.", False),
    (285, "My bad! 🙊 We missed the delivery. Click  <#1233350206280437760> to grab your refund 💵 and we’ll get things sorted out. Thanks for sticking with us! Kicker should join within 15 seconds, otherwise we will refund your money.", False),
    (300, "Our bad! We couldn’t get it to you on time. Expect a refund soon, and we’ll make sure it doesn’t happen again! Click here <#1233350206280437760> to refund.", False)
]

@tasks.loop(count=1)
async def send_scheduled_messages(channel):
    for delay, message, use_fact in messages:
        await asyncio.sleep(delay)
        try:
            if use_fact:
                message = await choose_random_fact()
                message = f"__Fun fact:__ \n{message}"
            await channel.send(message)
        except discord.HTTPException as e:
            print(f"Failed to send message to channel {channel}: {e}")

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
        print(f"Starting task {task_name}.")
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