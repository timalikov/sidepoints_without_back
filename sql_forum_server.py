import aiomysql
from dotenv import load_dotenv
import os

load_dotenv()

class ForumsOfServerDatabase:
    HOST = os.getenv('HOST').strip()
    USER = os.getenv('USER_AWS').strip()
    PASSWORD = os.getenv('PASSWORD').strip()
    DATABASE = os.getenv('DATABASE').strip()

    @staticmethod
    async def get_pool():
        return await aiomysql.create_pool(
            host=ForumsOfServerDatabase.HOST,
            user=ForumsOfServerDatabase.USER,
            password=ForumsOfServerDatabase.PASSWORD,
            db=ForumsOfServerDatabase.DATABASE,
            autocommit=True
        )

    @staticmethod
    async def get_forums_by_server(server_id):
        pool = await ForumsOfServerDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "SELECT forum_id FROM forums_of_server WHERE server_id = %s;"
                await cursor.execute(query, (server_id,))
                results = await cursor.fetchall()
                forum_ids = [result[0] for result in results]
        pool.close()
        await pool.wait_closed()
        return forum_ids

    @staticmethod
    async def add_forum(server_id, forum_id):
        pool = await ForumsOfServerDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "INSERT INTO forums_of_server (server_id, forum_id) VALUES (%s, %s);"
                await cursor.execute(query, (server_id, forum_id))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def get_all_server_ids():
        pool = await ForumsOfServerDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "SELECT DISTINCT server_id FROM forums_of_server;"
                await cursor.execute(query)
                results = await cursor.fetchall()
                server_ids = [result[0] for result in results]
        pool.close()
        await pool.wait_closed()
        return server_ids
