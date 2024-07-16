import asyncpg
from contextlib import asynccontextmanager

class Wallets_Database:
    HOST = "localhost"
    PORT = 55432
    USER = "discord_bot"
    PASSWORD = "04fbe9e132dd9e6f1c25f0733e69a6aae83a7b58ace284f390b7cb4551ac1612"
    DATABASE = "ebdb"
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
