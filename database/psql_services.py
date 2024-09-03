from typing import List, Union

import asyncio
import asyncpg
import discord
from config import HOST_PSQL, USER_PSQL, PASSWORD_PSQL, DATABASE_PSQL, PORT_PSQL
from contextlib import asynccontextmanager
from database.core_kicker_list import kickers, managers

from models.thread_forum import find_thread_in_forum
from models.post_forum import Post_FORUM
from serializers.profile_serializer import serialize_profile_data
from database.fact_list import facts


APP_CHOICES = {
    "ALL": None,
    "BUDDY": "57c86488-8935-4a13-bae0-5ca8783e205d",
    "COACHING": "88169d78-85b4-4fa3-8298-3df020f13a6f",
    "JUST_CHATTING": "2974b0e8-69de-4a13-bae0-5ca8783e205d",
    "MOBILE": "439d8a72-8b8b-4a56-bb32-32c6e5d918ec",
    "Watch Youtube": "d3ae39d2-fd86-41d7-bc38-0b582ce338b5",
    "Play Games": "79bf303a-318b-4815-bd56-7b0b49ae7bff",
    "Virtual Date": "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9"
}

class Services_Database:
    HOST = HOST_PSQL
    PORT = PORT_PSQL
    USER = USER_PSQL
    PASSWORD = PASSWORD_PSQL
    DATABASE = DATABASE_PSQL
    CHUNK_SIZE = 10  # Number of rows to fetch at a time
    BASE_QUERY = "SELECT * FROM discord_services WHERE profile_score >= 100"

    def __init__(self, app_choice="ALL", user_name=None):
        self.current_offset = 0
        self.current_chunk = []
        self.app_choice = app_choice
        self.user_name = user_name

    async def get_pool(self):
        return await asyncpg.create_pool(
            host=self.HOST,
            port=self.PORT,
            user=self.USER,
            password=self.PASSWORD,
            database=self.DATABASE,
            min_size=1,
            max_size=20
        )

    @asynccontextmanager
    async def get_connection(self):
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            yield conn
        await pool.close()

    async def fetch_chunk(self):
        async with self.get_connection() as conn:
            if self.user_name:
                # Fetch user-specific services first
                query_user = """
                SELECT * FROM discord_services
                WHERE LOWER(profile_username) = LOWER($1)
                LIMIT $2 OFFSET $3;
                """
                user_chunk = await conn.fetch(query_user, self.user_name, self.CHUNK_SIZE, self.current_offset)
                self.current_chunk.extend(user_chunk)

            # Fetch remaining services if user-specific services are less than CHUNK_SIZE
            remaining_chunk_size = self.CHUNK_SIZE - len(self.current_chunk)
            if remaining_chunk_size > 0:
                default_query = self.BASE_QUERY
                query_args: List = []
                if self.app_choice == "ALL":
                    if self.user_name:
                        default_query += " AND profile_username != $1 LIMIT $2 OFFSET $3;"
                        query_args = [self.user_name, remaining_chunk_size, self.current_offset]
                    else:
                        default_query += " LIMIT $1 OFFSET $2;"
                        query_args = [remaining_chunk_size, self.current_offset]
                else:
                    if self.user_name:
                        default_query += " AND service_type_id = $1 AND profile_username != $2 LIMIT $3 OFFSET $4;"
                        query_args = [APP_CHOICES[self.app_choice], self.user_name, remaining_chunk_size, self.current_offset]
                    else:
                        default_query += " AND service_type_id = $1 LIMIT $2 OFFSET $3;"
                        query_args = [APP_CHOICES[self.app_choice], remaining_chunk_size, self.current_offset]
                default_query = default_query.replace("LIMIT", "ORDER BY profile_score LIMIT")
                remaining_chunk = await conn.fetch(default_query, *query_args)
                self.current_chunk.extend(remaining_chunk)

        self.current_offset += self.CHUNK_SIZE
        return self.current_chunk

    async def get_next_service(self):
        if not self.current_chunk:
            chunk = await self.fetch_chunk()
            if not chunk:
                return []
        result = self.current_chunk.pop(0)
        return serialize_profile_data(result)
    
    async def start_posting(
        self,
        forum_channel: discord.ForumChannel,
        guild: discord.Guild,
        bot
    ) -> None:
        for _ in range(100):
            profile_data = await self.get_next_service()
            if not profile_data:
                break
            thread: Union[bool, discord.Thread] = await find_thread_in_forum(
                guild=guild, forum=forum_channel, profile_data=profile_data
            )
            if thread and thread.archived:
                await thread.edit(archived=False)
            temp_post = Post_FORUM(bot, profile_data, forum_channel, thread)
            await temp_post.post_user_profile()
            await asyncio.sleep(4)

    async def get_services_by_discordId(self, discordId):
        async with self.get_connection() as conn:
            query = "SELECT * FROM discord_services WHERE discord_id = $1;"
            services = await conn.fetch(query, discordId)
        return services
    
    async def get_services_by_username(self, username):
        async with self.get_connection() as conn:
            if self.app_choice == "ALL":
                query = "SELECT * FROM discord_services WHERE profile_username ILIKE $1 LIMIT 1;"
                query_args = [username]
            else:
                query = "SELECT * FROM discord_services WHERE profile_username ILIKE $1 AND service_type_id = $2 LIMIT 1;"
                query_args = [username, APP_CHOICES[self.app_choice]]
            services = await conn.fetch(query, *query_args)
        return services.pop(0) if services else None

    async def get_service_type_name(self, service_type_id):
        async with self.get_connection() as conn:
            query = "SELECT name FROM discord_service_types WHERE id = $1;"
            service_type = await conn.fetchval(query, service_type_id)
        return service_type if service_type else "Unknown"

    async def get_channel_ids(self):
        async with self.get_connection() as conn:
            query = "SELECT channel_id FROM discord_server_channels;"
            records = await conn.fetch(query)
        return records

    async def get_all_active_tags(self):
        default_query = \
            self.BASE_QUERY.replace("*", "service_type_name") + " GROUP BY service_type_name"
        async with self.get_connection() as conn:
            tags = await conn.fetch(default_query)
        return [tag["service_type_name"] for tag in tags]
    
    async def get_kickers(self):
        return kickers
    
    async def get_managers(self):
        return managers

    async def get_facts(self):
        return facts