# import discord
# import mysql.connector
# from dotenv import load_dotenv
# import os
# import uuid
# load_dotenv()
#
#
# class Order_Database:
#     HOST = os.getenv('HOST').strip()
#     USER = os.getenv('USER_AWS').strip()
#     PASSWORD = os.getenv('PASSWORD').strip()
#     DATABASE = os.getenv('DATABASE').strip()
#
#
#     @staticmethod
#     def get_connection():
#         return mysql.connector.connect(
#             host=Order_Database.HOST,
#             user=Order_Database.USER,
#             password=Order_Database.PASSWORD,
#             database=Order_Database.DATABASE
#         )
#
#     @staticmethod
#     async def get_order_data(order_id):
#         conn = Order_Database.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         query = "SELECT * FROM kicker_order WHERE order_id = %s;"
#         cursor.execute(query, (order_id,))
#         result = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         return result
#
#     @staticmethod
#     async def set_user_data(data):
#         conn = Order_Database.get_connection()
#         cursor = conn.cursor()
#         # Generate a UUID
#         order_id = str(uuid.uuid4())
#         query = """INSERT INTO kicker_order (order_id, user_id, task_id, status, push_count, accept_count)
#                    VALUES (%s, %s, %s, %s, %s, %s)
#                    ON DUPLICATE KEY UPDATE
#                    user_id = VALUES(user_id),
#                    task_id = VALUES(task_id),
#                    status = VALUES(status),
#                    push_count = VALUES(push_count),
#                    accept_count = VALUES(accept_count);"""
#         cursor.execute(query, (
#             order_id,
#             data.get('user_id'),
#             data.get('task_id'),
#             data.get('status', 1),  # Default status to 1 if not provided
#             data.get('push_count', 0),  # Default push_count to 0 if not provided
#             data.get('accept_count', 0),  # Default accept_count to 0 if not provided
#         ))
#         conn.commit()
#         cursor.close()
#         conn.close()
#
#     @staticmethod
#     async def update_column(order_id, column, value):
#         conn = Order_Database.get_connection()
#         cursor = conn.cursor()
#         query = f"UPDATE kicker_order SET {column} = %s WHERE order_id = %s"
#         cursor.execute(query, (value, order_id))
#         conn.commit()
#         cursor.close()
#         conn.close()
#
#     @staticmethod
#     async def get_active_order_ids():
#         conn = Order_Database.get_connection()
#         cursor = conn.cursor()
#         query = "SELECT order_id FROM kicker_order WHERE status = 1;"
#         cursor.execute(query)
#         result = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return [row[0] for row in result]
#
#
#     @staticmethod
#     async def insert_push_order(order_id, user_id):
#         conn = Order_Database.get_connection()
#         cursor = conn.cursor()
#         query = """INSERT INTO push_order (order_id, user_id)
#                    VALUES (%s, %s);"""
#         cursor.execute(query, (order_id, user_id))
#         conn.commit()
#         cursor.close()
#         conn.close()
#
#     @staticmethod
#     async def get_pushed_user_ids(order_id):
#         conn = Order_Database.get_connection()
#         cursor = conn.cursor()
#         query = "SELECT user_id FROM push_order WHERE order_id = %s;"
#         cursor.execute(query, (order_id,))
#         result = cursor.fetchall()
#         cursor.close()
#         conn.close()
#         return [row[0] for row in result]
import discord
import aiomysql
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

class Order_Database:
    HOST = os.getenv('HOST').strip()
    USER = os.getenv('USER_AWS').strip()
    PASSWORD = os.getenv('PASSWORD').strip()
    DATABASE = os.getenv('DATABASE').strip()

    @staticmethod
    async def get_pool():
        return await aiomysql.create_pool(
            host=Order_Database.HOST,
            user=Order_Database.USER,
            password=Order_Database.PASSWORD,
            db=Order_Database.DATABASE,
            autocommit=True
        )

    @staticmethod
    async def get_order_data(order_id):
        pool = await Order_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT * FROM kicker_order WHERE order_id = %s;"
                await cursor.execute(query, (order_id,))
                result = await cursor.fetchone()
        pool.close()
        await pool.wait_closed()
        return result

    @staticmethod
    async def set_user_data(data):
        pool = await Order_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                order_id = str(uuid.uuid4())
                query = """INSERT INTO kicker_order (order_id, user_id, task_id, status, push_count, accept_count) 
                           VALUES (%s, %s, %s, %s, %s, %s) 
                           ON DUPLICATE KEY UPDATE 
                           user_id = VALUES(user_id), 
                           task_id = VALUES(task_id), 
                           status = VALUES(status), 
                           push_count = VALUES(push_count),
                           accept_count = VALUES(accept_count);"""
                await cursor.execute(query, (
                    order_id,
                    data.get('user_id'),
                    data.get('task_id'),
                    data.get('status', 1),  # Default status to 1 if not provided
                    data.get('push_count', 0),  # Default push_count to 0 if not provided
                    data.get('accept_count', 0)  # Default accept_count to 0 if not provided
                ))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def update_column(order_id, column, value):
        pool = await Order_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = f"UPDATE kicker_order SET {column} = %s WHERE order_id = %s"
                await cursor.execute(query, (value, order_id))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def get_active_order_ids():
        pool = await Order_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT order_id FROM kicker_order WHERE status = 1;"
                await cursor.execute(query)
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return [row['order_id'] for row in result]

    @staticmethod
    async def insert_push_order(order_id, user_id):
        pool = await Order_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "INSERT INTO push_order (order_id, user_id) VALUES (%s, %s);"
                await cursor.execute(query, (order_id, user_id))
                await conn.commit()
        pool.close()
        await pool.wait_closed()

    @staticmethod
    async def get_pushed_user_ids(order_id):
        pool = await Order_Database.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                query = "SELECT user_id FROM push_order WHERE order_id = %s;"
                await cursor.execute(query, (order_id,))
                result = await cursor.fetchall()
        pool.close()
        await pool.wait_closed()
        return [row['user_id'] for row in result]
