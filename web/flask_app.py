import asyncio
import csv
import datetime
from enum import Enum
import io
import logging
import uuid

from flask import Flask, request, jsonify, Response
import config
from services.messages.base import (
    send_confirm_order_message,
    send_discord_notification,
    send_boost_message,
    send_kickers_reaction_test,
    send_order_message
)
from models.private_channel import create_private_discord_channel
from bot_instance import get_bot
from models.enums import Gender, Languages
import discord
from services.cache.client import custom_cache

main_guild_id = config.MAIN_GUILD_ID
bot = get_bot()
app = Flask(__name__)
app.logger.setLevel(logging.ERROR)

@app.route('/discord_api/server_user_counts', methods=['GET'])
async def server_user_counts():
    user_counts = {}
    total_members = 0
    for guild in bot.guilds:
        user_counts[guild.id] = {
            "guild_name": guild.name,
            "member_count": guild.member_count
        }
    return jsonify(user_counts), 200


@app.route("/discord_api/notification", methods=['POST'])
async def send_notification():
    data = request.json
    try:
        user_id: int = int(data["discordId"]) if data.get("type") == "message" else data["kickerDiscordId"]
        message: str = data["message"]
    except KeyError as e:
        return jsonify({"message": f"Missing key: {e}"}), 400
    future = asyncio.run_coroutine_threadsafe(send_discord_notification(user_id=user_id, message=message), bot.loop)
    is_user_found = future.result()
    if not is_user_found:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"message": "Notification sended"}), 200


@app.route("/discord_api/reaction_test", methods=['POST'])
def reaction_test():
    future = asyncio.run_coroutine_threadsafe(send_kickers_reaction_test(), bot.loop)
    success = future.result()
    if success:
        return jsonify({"message": "ok"}), 200
    return jsonify({"error": "Just error"}), 400


@app.route("/discord_api/order/choice", methods=['POST'])
def new_order_choice():
    data: dict = request.json
    order_id: uuid.UUID = data["orderId"]
    tag_name: str = data["tagNames"][0] if data["tagNames"] else None
    language: str = data["languages"][0] if data["languages"] else None
    gender = data.get("gender") 
    description: str = data.get("description")

    language = language if language else Languages.UNIMPORTANT.value
    gender: str = Gender[gender].value if gender in Gender.__members__ else Gender.UNIMPORTANT.value

    future = asyncio.run_coroutine_threadsafe(
        send_order_message(order_id=order_id, tag_name=tag_name, language=language, gender=gender, extra_text=description), 
        bot.loop
    )
    success = future.result()
    if success:
        return jsonify({"message": "ok"}), 200
    return jsonify({"error": "Just error"}), 400
    

@app.route('/discord_api/boost', methods=['POST'])
async def boost_compleate():
    data: dict = request.json
    image_url = data.get("imageUrl")
    message = data.get("message", "")
    if not image_url:
        return jsonify({"error": "Missing field: image_url."}), 400
    future = asyncio.run_coroutine_threadsafe(
        send_boost_message(
            image_url=image_url,
            message=message
        ),
        bot.loop
    )
    success, errors = future.result()
    if success:
        return jsonify({"message": "Send boost notification"}), 200
    else:
        return jsonify({"error": errors}), 400

    
@app.route('/discord_api/health_check', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route('/discord_api/order/confirm', methods=['POST'])
async def handle_confirm_order():
    data: dict = request.json
    customerId: str = data.get("customerId")
    serviceName = data.get("serviceName")
    kickerId: str = data.get("kickerId")
    kickerUsername: str = data.get("kickerUsername")
    purchaseId: str = data.get("purchaseId")
    discord_server_id: int = data.get("discordServerId")

    is_channel_created = custom_cache.get_purchase_id(purchaseId)
    if is_channel_created:
        return jsonify({"message": "Private channel created before sqs"}), 200
    
    try:
        challenger: discord.User = await asyncio.wrap_future(
            asyncio.run_coroutine_threadsafe(bot.fetch_user(int(customerId)), bot.loop)
        )
        challenged: discord.User = await asyncio.wrap_future(
            asyncio.run_coroutine_threadsafe(bot.fetch_user(int(kickerId)), bot.loop)
        )

    except discord.NotFound:
        return jsonify({"error": "One or more users could not be found in this guild."}), 400
    except Exception as e:
        return jsonify({"error": f"Error fetching users: {str(e)}"}), 500

    try:
        success, response = await asyncio.wrap_future(
            asyncio.run_coroutine_threadsafe(
                send_confirm_order_message(
                    customer=challenger,
                    kicker=challenged,
                    kicker_username=kickerUsername,
                    service_name=serviceName,
                    purchase_id=purchaseId,
                    discord_server_id=int(discord_server_id)
                ),
                bot.loop
            )
        )

        if success:
            return jsonify({"message": "Private channel created", "channel_id": response}), 200
        else:
            return jsonify({"error": response}), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/discord_api/get_guild_members', methods=['GET'])
async def handle_get_guild_members():
    guild_ids = config.GUILDS_TO_GET_MEMBER_COUNT
    guild_members = {}
    for guild_id in guild_ids:
        guild = bot.get_guild(guild_id)
        if guild:
            try:
                guild_members[guild.name] = guild.member_count
            except AttributeError:
                guild_members[guild.name] = "Unable to fetch member count"
        else:
            guild_members[guild.name] = "Guild not found"

    return jsonify(guild_members), 200

@app.route('/discord_api/create_private_channel', methods=['POST'])
async def handle_create_private_channel():
    data = request.json
    channelName = data.get('channelName')
    customerId = data.get("customerId")
    kickerId = data.get("kickerId")
    serviceName = data.get("serviceName")
    kickerUsername = data.get("kickerUsername")
    if channelName:
        channel_name = f"private-channel-{channelName}"
        guild_id = main_guild_id
        guild = bot.get_guild(guild_id)
        try:
            challenger = guild.get_member(int(customerId))
            challenged = guild.get_member(int(kickerId))
        except ValueError as e:
            print(f"Int error: {e}")
            return

        if not all([challenger, challenged]):
            return jsonify({"error": "One or more users could not be found in this guild."}), 400
        future = asyncio.run_coroutine_threadsafe(create_private_discord_channel(bot, guild_id, channel_name, challenger, challenged, serviceName, kickerUsername), bot.loop)
        success, response = future.result()  # This blocks until the coroutine completes

        if success:
            return jsonify({"message": "Private channel created", "channel_id": response.id}), 200
        else:
            return jsonify({"error": response.id}), 400
    else:
        return jsonify({"error": "Challenge ID not provided"}), 400


def create_app():
    return app
