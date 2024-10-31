from database.dto.base import BasePsqlDTO


class DiscordGuildChannelsDTO(BasePsqlDTO):
    """
    DiscordGuildChannelsDTO!

    Info: 
        schema: discord_bot;
        locate: tables;
        name: guild_channels.
    Fields:
        id: int
        guild_id: int
        channel_id: int
        channel_name: varchar
    """

    BASE_QUERY = "SELECT * FROM discord_bot.guild_channels"

    async def get_channel_id_by_name(self, guild_id: int, channel_name: str) -> int:
        async with self.get_connection() as conn:
            query = self.BASE_QUERY.replace("*", "channel_id") + " WHERE guild_id = $1 AND channel_name = $2"
            channels = await conn.fetch(query, guild_id, channel_name)
        try:
            channel = channels[0]["channel_id"]
        except (IndexError, KeyError):
            channel = None
        return channel
    
    async def create(self, guild_id: int, channel_name: str, channel_id: int) -> str:
        async with self.get_connection() as conn:
            query = (
                "INSERT INTO discord_bot.guild_channels "
                "(guild_id, channel_name, channel_id) "
                "VALUES ($1, $2, $3)"
            )
            new_row = await conn.fetch(query, guild_id, channel_name, channel_id)
        return new_row
    
    async def delete(self, channel_id: int) -> str:
        async with self.get_connection() as conn:
            query = "DELETE FROM discord_bot.guild_channels WHERE channel_id = $1"
            new_row = await conn.fetch(query, channel_id)
        return new_row
