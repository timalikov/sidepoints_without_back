# import discord
# import mysql.connector
# from dotenv import load_dotenv
# import os
# load_dotenv()
#
#
# class Profile_Database:
#     HOST = os.getenv('HOST').strip()
#     USER = os.getenv('USER_AWS').strip()
#     PASSWORD = os.getenv('PASSWORD').strip()
#     DATABASE = os.getenv('DATABASE').strip()
#
#
#     @staticmethod
#     def get_connection():
#         return mysql.connector.connect(
#             host=Profile_Database.HOST,
#             user=Profile_Database.USER,
#             password=Profile_Database.PASSWORD,
#             database=Profile_Database.DATABASE
#         )
#
#     @staticmethod
#     async def get_user_data(user_id):
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         query = "SELECT * FROM profiles WHERE user_id = %s;"
#         cursor.execute(query, (str(user_id),))
#         result = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         return result
#
#
#     @staticmethod
#     async def set_user_data(data):
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor()
#         query = """INSERT INTO profiles (user_id, name, user_picture, about, price, discord_username, wallet)
#                    VALUES (%s, %s, %s, %s, %s, %s, %s)
#                    ON DUPLICATE KEY UPDATE
#                    name = VALUES(name),
#                    user_picture = VALUES(user_picture),
#                    about = VALUES(about),
#                    price = VALUES(price),
#                    discord_username = VALUES(discord_username),
#                    wallet = VALUES(wallet);"""
#         cursor.execute(query, (
#             data.get('user_id'),
#             data.get('name'),
#             data.get('user_picture'),
#             # data.get('gender'),
#             # data.get('age'),
#             data.get('about'),
#             data.get('price'),
#             data.get('discord_username'),
#             data.get('wallet')
#         ))
#         conn.commit()
#         cursor.close()
#         conn.close()
#
#     @staticmethod
#     async def get_all_user_ids():
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         query = "SELECT user_id FROM profiles;"
#         cursor.execute(query)
#         result = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return [row['user_id'] for row in result]
#
#     @staticmethod
#     async def get_profile_at_index(index):
#         user_ids = Profile_Database.get_all_user_ids()
#         if user_ids:
#             user_id = user_ids[index % len(user_ids)]
#             return Profile_Database.get_user_data(user_id)
#         return None
#
#     @staticmethod
#     def get_next_user_data_excluding_user_id(start_index, exclude_user_id):
#         user_ids = Profile_Database.get_all_user_ids()
#         if not user_ids:
#             return None
#
#         # Adjust the start_index based on the length of the user_ids list
#         adjusted_index = start_index % len(user_ids)
#
#         # Try to find the next user profile that does not match the exclude_user_id
#         for _ in range(len(user_ids)):  # Ensure we don't loop indefinitely
#             potential_user_id = user_ids[adjusted_index]
#             if potential_user_id != exclude_user_id:
#                 return Profile_Database.get_user_data(potential_user_id)
#             adjusted_index = (adjusted_index + 1) % len(user_ids)  # Move to the next index, wrap around if necessary
#
#         # If all user_ids are the same as exclude_user_id or no different user found, return None
#         return None
#
#     @staticmethod
#     def add_wallet(user_id, wallet_value):
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         # Check if the user exists and if so, update or insert the wallet value
#         query = """
#         INSERT INTO profiles (user_id, wallet)
#         VALUES (%s, %s)
#         ON DUPLICATE KEY UPDATE wallet = VALUES(wallet);
#         """
#
#         try:
#             cursor.execute(query, (user_id, wallet_value))
#             conn.commit()
#             return True
#         except mysql.connector.Error as err:
#             print(f"Error: {err}")
#             return False
#         finally:
#             cursor.close()
#             conn.close()
#
#     @staticmethod
#     async def check_presence_and_send_invite(interaction: discord.Interaction, user_id: int, guild_id: int):
#         target_guild = interaction.client.get_guild(guild_id)
#         if not target_guild:
#             # Respond or follow-up to interaction based on whether you've already responded
#             await interaction.response.send_message("Target guild not found.", ephemeral=True)
#             return False
#
#         member = target_guild.get_member(user_id)
#         if member:
#             return True
#         else:
#             # The member does not exist in the target guild
#             # Respond or follow-up to interaction based on whether you've already responded
#             # This assumes you have not responded to the interaction yet
#             await interaction.response.defer(ephemeral=True)
#
#             for channel in target_guild.text_channels:
#                 if channel.permissions_for(target_guild.me).create_instant_invite:
#                     invite = await channel.create_invite(reason="Inviting user to join guild")
#                     await interaction.followup.send(f"User not found in the target guild. Here is an invite link to join: {invite.url}", ephemeral=True)
#                     return False
#
#             await interaction.followup.send("Unable to create an invite link. No suitable channel found.", ephemeral=True)
#             return False
#
#     @staticmethod
#     async def get_user_ids_by_task_id(task_id):
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         # Now we're selecting from the 'profile_task' table
#         query = "SELECT user_id FROM profile_task WHERE task_id = %s;"
#         cursor.execute(query, (task_id,))
#         result = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return [row['user_id'] for row in result]
#
#     @staticmethod
#     async def get_user_task_by_user_id(user_id):
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         # Selecting the first task description for the given user_id
#         query = "SELECT task_desc FROM profile_task WHERE user_id = %s LIMIT 1;"
#         cursor.execute(query, (user_id,))
#         result = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         # Return the task description if a task is found, otherwise return None
#         return result['task_desc'] if result else "No category"
#
#
#     @staticmethod
#     async def get_user_data_by_username(username):
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         query = "SELECT * FROM profiles WHERE LOWER(name) = %s;"
#         cursor.execute(query, (username,))
#         results = cursor.fetchall()  # Fetch all results that match the query
#         cursor.close()
#         conn.close()
#         return results  # This will return a list of dictionaries
#
#
#     @staticmethod
#     async def get_channel_id_by_user_id(user_id):
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         query = "SELECT channel_id FROM owned_channel WHERE user_id = %s;"
#         cursor.execute(query, (user_id,))
#         result = cursor.fetchall()  # Using fetchall to get all rows in case there are multiple channels per user
#         cursor.close()
#         conn.close()
#         return [row['channel_id'] for row in result]  # Returning a list of channel IDs
#
#     @staticmethod
#     async def add_channel_to_user(user_id, channel_id):
#         """ Adds or updates a channel ID for a given user in the owned_channel table. """
#         conn = Profile_Database.get_connection()
#         cursor = conn.cursor()
#         query = """
#         INSERT INTO owned_channel (user_id, channel_id)
#         VALUES (%s, %s)
#         ON DUPLICATE KEY UPDATE channel_id = VALUES(channel_id);
#         """
#         try:
#             cursor.execute(query, (str(user_id), channel_id))
#             conn.commit()
#             return True
#         except mysql.connector.Error as err:
#             print(f"Database error: {err}")
#             return False
#         finally:
#             cursor.close()
#             conn.close()
#
import random
import aiomysql
import discord
from dotenv import load_dotenv
import os

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

    # @staticmethod
    # async def get_all_users_with_priority():
    #     pool = await Profile_Database.get_pool()
    #     async with pool.acquire() as conn:
    #         async with conn.cursor(aiomysql.DictCursor) as cursor:
    #             query = "SELECT user_id FROM profiles ORDER BY priority;"
    #             await cursor.execute(query)
    #             result = await cursor.fetchall()
    #     pool.close()
    #     await pool.wait_closed()
    #     return [row['user_id'] for row in result]

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


