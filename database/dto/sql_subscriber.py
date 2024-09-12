import os
import aiomysql

class Subscribers_Database:
    HOST = os.getenv('HOST').strip()
    USER = os.getenv('USER_AWS').strip()
    PASSWORD = os.getenv('PASSWORD').strip()
    DATABASE = os.getenv('DATABASE').strip()

    @staticmethod
    async def get_pool():
        return await aiomysql.create_pool(
            host=Subscribers_Database.HOST,
            user=Subscribers_Database.USER,
            password=Subscribers_Database.PASSWORD,
            db=Subscribers_Database.DATABASE,
            autocommit=True
        )

    @staticmethod
    async def set_user_data(discord_id):
        pool = await Subscribers_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """INSERT INTO subscribers (discord_id) 
                           VALUES (%s) 
                           ON DUPLICATE KEY UPDATE 
                           discord_id = VALUES(discord_id);"""
                await cursor.execute(query, (
                    discord_id,
                ))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def get_all_discord_ids():
        pool = await Subscribers_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT discord_id FROM subscribers;"
                await cursor.execute(query)
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return [row['discord_id'] for row in result]

    @staticmethod
    async def delete_user_data(discord_id):
        pool = await Subscribers_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "DELETE FROM subscribers WHERE discord_id = %s;"
                await cursor.execute(query, (discord_id,))
                await conn.commit()
        pool.close()
        await pool.wait_closed()
