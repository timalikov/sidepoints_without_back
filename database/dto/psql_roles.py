from database.dto.base import BasePsqlDTO

class RolesDTO(BasePsqlDTO): 
    async def get_role_id_by_tag(self, tag: str, guild_id: int) -> int:
        async with self.get_connection() as conn:
            query = "SELECT role_id FROM tag_roles WHERE tag = $1 AND guild_id = $2"
            role_id = await conn.fetchval(query, tag, guild_id)
        return role_id
    
    async def save_role_id_by_tag(self, tag: str, guild_id: int, role_id: int) -> None:
        async with self.get_connection() as conn:
            query = "INSERT INTO tag_roles (tag, guild_id, role_id) VALUES ($1, $2, $3)"
            await conn.execute(query, tag, guild_id, role_id)