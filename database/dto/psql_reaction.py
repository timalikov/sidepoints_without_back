from datetime import datetime

from database.dto.base import BasePsqlDTO


class ReactionDTO(BasePsqlDTO):
    async def add_reaction(self, discord_id: int, seconds: int, created_at: datetime):
        async with self.get_connection() as conn:
            query = "INSERT INTO discord_bot.reaction_times (user_id, reaction_time, created_at) VALUES ($1, $2, $3)"
            services = await conn.fetch(query, discord_id, seconds, created_at)
        return services