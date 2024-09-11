import asyncio
import csv
import datetime
import io
from flask import Flask, request, jsonify, Response
import config
from services.messages.base import (
    send_confirm_order_message,
    send_discord_notification,
    send_boost_message,
    send_kickers_reaction_test
)
from models.private_channel import create_private_discord_channel
from sql_challenge import SQLChallengeDatabase
from bot_instance import get_bot

import discord

main_guild_id = config.MAIN_GUILD_ID
bot = get_bot()
app = Flask(__name__)

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
        user_id: int = data["kickerDiscordId"]
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


@app.route('/discord_ap/order/confirm', methods=['POST'])
async def handle_confirm_order():
    data: dict = request.json
    channelName: str = data.get('channelName')
    customerId: str = data.get("customerId")
    serviceName = data.get("serviceName")
    kickerId: str = data.get("kickerId")
    kickerUsername: str = data.get("kickerUsername")
    if channelName:
        channel_name = f"private-channel-{channelName}"
        challenger: discord.User = bot.get_user(int(customerId))
        challenged: discord.User = bot.get_user(int(kickerId))
        if not all([challenger, challenged]):
            return jsonify({"error": "One or more users could not be found in this guild."}), 400
        future = asyncio.run_coroutine_threadsafe(
            send_confirm_order_message(
                channel_name=channel_name,
                customer=challenger,
                kicker=challenged,
                kicker_username=kickerUsername,
                service_name=serviceName
            ),
            bot.loop
        )
        success, response = future.result()  # This blocks until the coroutine completes

        if success:
            return jsonify({"message": "Private channel created", "channel_id": response.id}), 200
        else:
            return jsonify({"error": response.id}), 400
    else:
        return jsonify({"error": "Challenge ID not provided"}), 400


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
        challenger = guild.get_member(int(customerId))
        challenged = guild.get_member(int(kickerId))

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


@app.route('/discord_api/challenges_last_week', methods=['GET'])
def get_challenges_last_week():
    # Get the 'days' parameter from the query string, defaulting to 7 if not provided
    days = request.args.get('days', default=7, type=int)

    # Calculate the date 'days' ago from today
    days_ago = datetime.now() - datetime.timedelta(days=days)
    days_ago_str = days_ago.strftime('%Y-%m-%d')

    # Open database connection and prepare cursor
    conn = SQLChallengeDatabase.get_connection()
    cursor = conn.cursor(dictionary=True)

    # SQL query to join challenges with profiles to fetch discord_username
    query = """
    SELECT c.challenge_id, c.user_id1, c.user_id2, c.date, c.price, c.channel_created, c.wallet, p.discord_username
    FROM challenges c
    LEFT JOIN profiles p ON c.user_id1 = p.user_id
    WHERE c.date >= %s;
    """
    cursor.execute(query, (days_ago_str,))

    # Fetch all matching records
    challenges = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create an in-memory output file for the CSV data
    si = io.StringIO()
    cw = csv.writer(si)
    # Write CSV headers including the new discord_username column
    cw.writerow(['challenge_id', 'user_id1', 'discord_username', 'user_id2', 'date', 'price', 'channel_created', 'wallet'])
    # Write data rows including the fetched discord_username
    for challenge in challenges:
        cw.writerow([
            challenge['challenge_id'],
            challenge['user_id1'],
            challenge['discord_username'],
            challenge['user_id2'],
            challenge['date'],
            challenge['price'],
            challenge['channel_created'],
            challenge['wallet']
        ])

    # Set the output file to return as an attachment
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = "attachment; filename=challenges_since_{days}_days_ago.csv".format(days=days)
    return output

def create_app():
    return app
