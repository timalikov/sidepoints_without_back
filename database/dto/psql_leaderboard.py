from database.dto.base import BasePsqlDTO


class LeaderboardDatabase(BasePsqlDTO):
    """
    LeaderboardDatabase!

    Info: 
        schema: public;
        locate: views;
        name: bot_leaderboard.
    """

    BASE_QUERY = "SELECT * FROM bot_leaderboard WHERE leaderboard_type = 'POINTS' "

    async def all(self):
        async with self.get_connection() as conn:
            query = self.BASE_QUERY + "ORDER BY total_pos LIMIT 20;"
            leaders = await conn.fetch(query)
        return leaders
