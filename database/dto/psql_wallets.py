import asyncpg
from contextlib import asynccontextmanager
from config import HOST_PSQL, USER_PSQL, PASSWORD_PSQL, DATABASE_PSQL, PORT_PSQL

from database.dto.base import BasePsqlDTO


class Wallets_Database(BasePsqlDTO):
    CHUNK_SIZE = 10  # Number of rows to fetch at a time

    def __init__(self, app_choice="ALL"):
        self.current_offset = 0
        self.current_chunk = []
        self.app_choice = app_choice

    async def get_wallet_by_discord_id(self, discord_id):
        async with self.get_connection() as conn:
            query = "SELECT crypto_wallet FROM discord_wallet WHERE discord = $1;"
            result = await conn.fetchrow(query, discord_id)
            if result:
                return result['crypto_wallet']
            else:
                return False
