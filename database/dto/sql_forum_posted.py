import aiomysql
from dotenv import load_dotenv
import os

load_dotenv()

class ForumUserPostDatabase:
    HOST = os.getenv('HOST').strip()
    USER = os.getenv('USER_AWS').strip()
    PASSWORD = os.getenv('PASSWORD').strip()
    DATABASE = os.getenv('DATABASE').strip()

    @staticmethod
    async def get_pool():
        return await aiomysql.create_pool(
            host=ForumUserPostDatabase.HOST,
            user=ForumUserPostDatabase.USER,
            password=ForumUserPostDatabase.PASSWORD,
            db=ForumUserPostDatabase.DATABASE,
            autocommit=True
        )

    @staticmethod
    async def add_forum_post(forum_id, thread_id, user_id, server_id):
        pool = await ForumUserPostDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """
                INSERT INTO forum_user_post (forum_id, thread_id, user_id, server_id)
                VALUES (%s, %s, %s, %s)
                """
                await cursor.execute(query, (forum_id, thread_id, user_id, server_id))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def get_thread_id_by_user_and_server(user_id, server_id):
        pool = await ForumUserPostDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT thread_id FROM forum_user_post WHERE user_id = %s AND server_id = %s;"
                await cursor.execute(query, (user_id, server_id))
                result = await cursor.fetchone()
        pool.close()
        await pool.wait_closed()
        return result["thread_id"] if result else None
    
    @staticmethod
    async def get_thread_id_by_user_and_forum_multi(user_id, forum_id):
        pool = await ForumUserPostDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT thread_id FROM forum_user_post WHERE user_id = %s AND forum_id = %s;"
                await cursor.execute(query, (user_id, forum_id))
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return [column["thread_id"] if column else None for column in result]

    @staticmethod
    async def delete_all_rows():
        pool = await ForumUserPostDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "DELETE FROM forum_user_post;"
                await cursor.execute(query)
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def delete_row_by_server_and_user(server_id, user_id):
        pool = await ForumUserPostDatabase.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "DELETE FROM forum_user_post WHERE server_id = %s AND user_id = %s;"
                await cursor.execute(query, (server_id, user_id))
                await conn.commit()
        pool.close()
        await pool.wait_closed()
