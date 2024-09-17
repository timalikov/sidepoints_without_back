import asyncpg
from config import HOST_PSQL, USER_PSQL, PASSWORD_PSQL, DATABASE_PSQL, PORT_PSQL
from contextlib import asynccontextmanager

from database.dto.interface import InterfaceDTO

class BasePsqlDTO(InterfaceDTO):
    HOST = HOST_PSQL
    PORT = PORT_PSQL
    USER = USER_PSQL
    PASSWORD = PASSWORD_PSQL
    DATABASE = DATABASE_PSQL

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
