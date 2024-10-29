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
    
    async def get_user_ranking(self, profile_id):
        async with self.get_connection() as conn:
            query = self.BASE_QUERY + "AND profile_id = $1;"
            user_ranking = await conn.fetchrow(query, profile_id)
        return user_ranking
