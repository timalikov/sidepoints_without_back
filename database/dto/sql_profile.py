import random
from datetime import datetime

import aiomysql
import discord
from dotenv import load_dotenv
import os

from services.logger.client import CustomLogger

logger = CustomLogger
load_dotenv()

class Profile_Database:
    HOST = os.getenv('HOST').strip()
    USER = os.getenv('USER_AWS').strip()
    PASSWORD = os.getenv('PASSWORD').strip()
    DATABASE = os.getenv('DATABASE').strip()

    @staticmethod
    async def get_pool():
        return await aiomysql.create_pool(
            host=Profile_Database.HOST,
            user=Profile_Database.USER,
            password=Profile_Database.PASSWORD,
            db=Profile_Database.DATABASE,
            autocommit=True
        )

    @staticmethod
    async def get_user_data(user_id):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT * FROM profiles WHERE user_id = %s;"
                await cursor.execute(query, (str(user_id),))
                result = await cursor.fetchone()
        pool.close()
        await pool.wait_closed()
        return result

    @staticmethod
    async def set_user_data(data):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """INSERT INTO profiles (user_id, name, user_picture, about, price, discord_username, wallet) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s) 
                           ON DUPLICATE KEY UPDATE 
                           name = VALUES(name), 
                           user_picture = VALUES(user_picture), 
                           about = VALUES(about), 
                           price = VALUES(price), 
                           discord_username = VALUES(discord_username),
                           wallet = VALUES(wallet);"""
                await cursor.execute(query, (
                    data.get('user_id'),
                    data.get('name'),
                    data.get('user_picture'),
                    data.get('about'),
                    data.get('price'),
                    data.get('discord_username'),
                    data.get('wallet')
                ))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def get_all_user_ids():
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT user_id FROM profiles;"
                await cursor.execute(query)
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return [row['user_id'] for row in result]

    @staticmethod
    async def get_profile_at_index(index):
        user_ids = await Profile_Database.get_all_user_ids()
        if user_ids:
            user_id = user_ids[index % len(user_ids)]
            return await Profile_Database.get_user_data(user_id)
        return None

    @staticmethod
    async def get_next_user_data_excluding_user_id(start_index, exclude_user_id):
        user_ids = await Profile_Database.get_all_user_ids()
        if not user_ids:
            return None

        adjusted_index = start_index % len(user_ids)

        for _ in range(len(user_ids)):
            potential_user_id = user_ids[adjusted_index]
            if potential_user_id != exclude_user_id:
                return await Profile_Database.get_user_data(potential_user_id)
            adjusted_index = (adjusted_index + 1) % len(user_ids)
        return None

    @staticmethod
    async def add_wallet(user_id, wallet_value):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """
                INSERT INTO profiles (user_id, wallet) 
                VALUES (%s, %s) 
                ON DUPLICATE KEY UPDATE wallet = VALUES(wallet);
                """
                await cursor.execute(query, (user_id, wallet_value))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def check_presence_and_send_invite(interaction: discord.Interaction, user_id: int, guild_id: int):
        target_guild = interaction.client.get_guild(guild_id)
        if not target_guild:
            await interaction.response.send_message("Target guild not found.", ephemeral=True)
            return False

        member = target_guild.get_member(user_id)
        if member:
            return True
        else:
            await interaction.response.defer(ephemeral=True)

            for channel in target_guild.text_channels:
                if channel.permissions_for(target_guild.me).create_instant_invite:
                    invite = await channel.create_invite(reason="Inviting user to join guild")
                    await interaction.followup.send(f"User not found in the target guild. Here is an invite link to join: {invite.url}", ephemeral=True)
                    return False

            await interaction.followup.send("Unable to create an invite link. No suitable channel found.", ephemeral=True)
            return False

    @staticmethod
    async def get_user_ids_by_task_id(task_id):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT user_id FROM profile_task WHERE task_id = %s;"
                await cursor.execute(query, (task_id,))
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return [row['user_id'] for row in result]

    @staticmethod
    async def get_user_task_by_user_id(user_id):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT task_desc FROM profile_task WHERE user_id = %s LIMIT 1;"
                await cursor.execute(query, (user_id,))
                result = await cursor.fetchone()
        pool.close()
        await pool.wait_closed()
        return result['task_desc'] if result else "No category"

    @staticmethod
    async def get_user_data_by_username(username):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT * FROM profiles WHERE LOWER(name) = %s;"
                await cursor.execute(query, (username,))
                results = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return results

    @staticmethod
    async def get_channel_id_by_user_id(user_id):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT channel_id FROM owned_channel WHERE user_id = %s;"
                await cursor.execute(query, (user_id,))
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return [row['channel_id'] for row in result]

    @staticmethod
    async def add_channel_to_user(user_id, channel_id):
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """
                INSERT INTO owned_channel (user_id, channel_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id);
                """
                await cursor.execute(query, (str(user_id), channel_id))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def get_all_users_with_priority():
        pool = await Profile_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT user_id, priority FROM profiles ORDER BY priority;"
                await cursor.execute(query)
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()

        # Shuffle users with the same priority
        from collections import defaultdict
        priority_groups = defaultdict(list)
        for row in result:
            priority_groups[row['priority']].append(row['user_id'])

        ordered_user_ids = []
        for priority in sorted(priority_groups.keys()):
            random.shuffle(priority_groups[priority])
            ordered_user_ids.extend(priority_groups[priority])

        return ordered_user_ids



# Function to log interactions to the database asynchronously
async def log_to_database(user_id, command_type):
    await logger.error_discord("The user id to be recorded: ", user_id)
    conn = await aiomysql.connect(
            host=os.getenv('HOST').strip(),
            user=os.getenv('USER_AWS').strip(),
            password=os.getenv('PASSWORD').strip(),
            db=os.getenv('DATABASE').strip(),
            autocommit=True
    )
    async with conn.cursor() as cursor:
        query = "INSERT INTO commands (datetime, user_id, command_type) VALUES (%s, %s, %s)"
        data = (datetime.now(), user_id, command_type)
        await cursor.execute(query, data)
        await conn.commit()
    conn.close()
