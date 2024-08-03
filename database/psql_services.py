import asyncio

import asyncpg
from config import HOST_PSQL, USER_PSQL, PASSWORD_PSQL, DATABASE_PSQL, PORT_PSQL
from contextlib import asynccontextmanager


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

    # async def fetch_chunk(self):
    #     async with self.get_connection() as conn:
    #         if self.user_name:
    #             query = "SELECT * FROM discord_services LIMIT $1 OFFSET $2 ORDER BY profile_username;"
    #             self.current_chunk = await conn.fetch(query, self.CHUNK_SIZE, self.current_offset)
    #         else:
    #             if self.app_choice == "ALL":
    #                 query = "SELECT * FROM discord_services LIMIT $1 OFFSET $2;"
    #                 self.current_chunk = await conn.fetch(query, self.CHUNK_SIZE, self.current_offset)
    #             else:
    #                 query = "SELECT * FROM discord_services WHERE service_type_id = $1 LIMIT $2 OFFSET $3;"
    #                 self.current_chunk = await conn.fetch(query, APP_CHOICES[self.app_choice], self.CHUNK_SIZE, self.current_offset)
    #     self.current_offset += self.CHUNK_SIZE
    #     return self.current_chunk

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
                if self.app_choice == "ALL":
                    query_all = "SELECT * FROM discord_services WHERE profile_username != $1 LIMIT $2 OFFSET $3;"
                    remaining_chunk = await conn.fetch(query_all, self.user_name, remaining_chunk_size, self.current_offset)
                else:
                    query_specific = """
                    SELECT * FROM discord_services
                    WHERE service_type_id = $1 AND profile_username != $2
                    LIMIT $3 OFFSET $4;
                    """
                    remaining_chunk = await conn.fetch(query_specific, APP_CHOICES[self.app_choice], self.user_name, remaining_chunk_size, self.current_offset)
                self.current_chunk.extend(remaining_chunk)

        self.current_offset += self.CHUNK_SIZE
        return self.current_chunk

    async def get_next_service(self):
        if not self.current_chunk:
            chunk = await self.fetch_chunk()
            if not chunk:
                return []
        result = self.current_chunk.pop(0)
        return result

    async def get_services_by_discord_id(self, discord_id):
        async with self.get_connection() as conn:
            query = "SELECT * FROM discord_services WHERE discord_id = $1;"
            services = await conn.fetch(query, discord_id)
        return services

# async def main():
#     # Create an instance of Services_Database with user_name "puppy"
#     services_db = Services_Database(user_name="Artur_Artur")
#
#     # Fetch the first chunk of data
#     await services_db.fetch_chunk()
#
#     # Continuously get the next service every 1 second
#     while True:
#         next_service = await services_db.get_next_service()
#
#         # If no more services are available, break the loop
#         if not next_service:
#             print("No more services available.")
#             break
#
#         # Print the next service
#         print(next_service)
#
#         # Wait for 1 second before fetching the next service
#         await asyncio.sleep(1)
#
# # Run the main function
# asyncio.run(main())
