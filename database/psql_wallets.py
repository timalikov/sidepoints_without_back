import asyncpg
from contextlib import asynccontextmanager
from config import HOST_PSQL, USER_PSQL, PASSWORD_PSQL, DATABASE_PSQL, PORT_PSQL

class Wallets_Database:
    HOST = HOST_PSQL
    PORT = PORT_PSQL
    USER = USER_PSQL
    PASSWORD = PASSWORD_PSQL
    DATABASE = DATABASE_PSQL
    CHUNK_SIZE = 10  # Number of rows to fetch at a time

    def __init__(self, app_choice="ALL"):
        self.current_offset = 0
        self.current_chunk = []
        self.app_choice = app_choice

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

    async def get_wallet_by_discord_id(self, discord_id):
        async with self.get_connection() as conn:
            query = "SELECT crypto_wallet FROM discord_wallet WHERE discord = $1;"
            result = await conn.fetchrow(query, discord_id)
            if result:
                return result['crypto_wallet']
            else:
                return False
