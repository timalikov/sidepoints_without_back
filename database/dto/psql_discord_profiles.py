from database.dto.base import BasePsqlDTO


class DiscordProfilesDTO(BasePsqlDTO):
    """
    NOT USED!!!!!!!!!!!!!!

    Info: 
        schema: public;
        locate: views;
        name: discord_profiles_all.
    Fields:
        id: uuid
        crypto_wallet: varchar
        discord: varchar
        discord_id: varchar
    """

    BASE_QUERY = "SELECT * FROM discord_profiles_all"

    async def get_wallet_by_discord_id(self, discord_id: int) -> str:
        async with self.get_connection() as conn:
            query = self.BASE_QUERY.replace("*", "crypto_wallet") + " WHERE discord_id = $1"
            wallets = await conn.fetch(query, str(discord_id))
        try:
            wallet = wallets[0]["crypto_wallet"]
        except (IndexError, KeyError):
            wallet = None
        return wallet