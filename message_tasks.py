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

@tasks.loop(count=1)
async def send_message_after_10_seconds(channel):
    await asyncio.sleep(10)
    try:
        await channel.send("🚀 Just a quick update: We're on it! Thanks for your patience! 🌟 Kicker should join within 5 minutes, otherwise we will refund your money.", 
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_20_seconds(channel):
    await asyncio.sleep(20)
    try:
        await channel.send("🔧 Our team is working their magic! Hang tight - we're almost there! Kicker should join within 4 minutes 40 seconds, otherwise we will refund your money.",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")
    
@tasks.loop(count=1)
async def send_message_after_40_seconds(channel):
    await asyncio.sleep(40)
    try:
        await channel.send("⏳ Thanks for sticking with us! We’re making progress, stay tuned! 🚀 Kicker should join within 4 minutes 20 seconds, otherwise we will refund your money.",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_60_seconds(channel):
    await asyncio.sleep(60)
    try:
        fact = await choose_random_fact()
        await channel.send(fact, view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_80_seconds(channel):
    await asyncio.sleep(80)
    try:
        await channel.send("💪 We’re on a mission to get this sorted for you! Thanks for your patience! 🙌 Kicker should join within 3 minutes 40 seconds, otherwise we will refund your money.",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_110_seconds(channel):
    await asyncio.sleep(110)
    try:
        await channel.send("🛠️ Almost there! Our team is busy behind the scenes. We appreciate your patience! 🎉 Kicker should join within 3 minutes 10 seconds, otherwise we will refund your money.",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_150_seconds(channel):
    await asyncio.sleep(150)
    try:
        await channel.send("🎯 We’re making strides! Thanks for hanging in there – we’ll be with you shortly! 🚀 Kicker should join within 2 minutes 30 seconds, otherwise we will refund your money.",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_180_seconds(channel):
    await asyncio.sleep(180)
    try:
        fact = await choose_random_fact()
        await channel.send(fact, view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_210_seconds(channel):
    await asyncio.sleep(210)
    try:
        await channel.send("✨ Just a little bit more time! We’re working hard to get everything sorted. Thanks! 💪 Kicker should join within 1 minute 30 seconds, otherwise we will refund your money. ",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_240_seconds(channel):
    await asyncio.sleep(240)
    try:
        await channel.send("🔍 Almost ready! Our team is doing their thing. Thanks for waiting! 🙌 Kicker should join within 1 minute, otherwise we will refund your money. ",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_255_seconds(channel):
    await asyncio.sleep(255)
    try:
        await channel.send("Oops! Looks like we hit a snag. We're on it and will make it right soon! 🙌 Kicker should join within 45 seconds, otherwise we will refund your money. ",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_270_seconds(channel):
    await asyncio.sleep(270)
    try:
        await channel.send("Oops! 😬 We hit a snag and couldn’t deliver. No worries – get your refund 💸 <#1233350206280437760>. Thanks for your patience! Kicker should join within 30 seconds, otherwise we will refund your money. ",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_285_seconds(channel):
    await asyncio.sleep(285)
    try:
        await channel.send("My bad! 🙊 We missed the delivery. Click  <#1233350206280437760> to grab your refund 💵 and we’ll get things sorted out. Thanks for sticking with us! Kicker should join within 15 seconds, otherwise we will refund your money. ",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

@tasks.loop(count=1)
async def send_message_after_300_seconds(channel):
    await asyncio.sleep(300)
    try:
        await channel.send("Our bad! We couldn’t get it to you on time. Expect a refund soon, and we’ll make sure it doesn’t happen again! Click here <#1233350206280437760> to refund.",
                           view=StopButton(stop_all_messages))
    except discord.HTTPException as e:
        print(f"Failed to send message to channel {channel}: {e}")

async def start_all_messages(channel):
    send_message_after_10_seconds.start(channel)
    send_message_after_20_seconds.start(channel)
    send_message_after_40_seconds.start(channel)
    send_message_after_60_seconds.start(channel)
    send_message_after_80_seconds.start(channel)
    send_message_after_110_seconds.start(channel)
    send_message_after_150_seconds.start(channel)
    send_message_after_180_seconds.start(channel)
    send_message_after_210_seconds.start(channel)
    send_message_after_240_seconds.start(channel)
    send_message_after_255_seconds.start(channel)
    send_message_after_270_seconds.start(channel)
    send_message_after_285_seconds.start(channel)
    send_message_after_300_seconds.start(channel)


async def stop_all_messages():
    send_message_after_10_seconds.stop()
    send_message_after_20_seconds.stop()
    send_message_after_40_seconds.stop()
    send_message_after_60_seconds.stop()
    send_message_after_80_seconds.stop()
    send_message_after_110_seconds.stop()
    send_message_after_150_seconds.stop()
    send_message_after_180_seconds.stop()
    send_message_after_210_seconds.stop()
    send_message_after_240_seconds.stop()
    send_message_after_255_seconds.stop()
    send_message_after_270_seconds.stop()
    send_message_after_285_seconds.stop()
    send_message_after_300_seconds.stop()
    return True