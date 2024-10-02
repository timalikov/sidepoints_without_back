from typing import List, Literal

from database.core_kicker_list import managers

from serializers.profile_serializer import serialize_profile_data
from database.fact_list import facts
from database.dto.base import BasePsqlDTO


APP_CHOICES = {
    "ALL": None,
    "BUDDY": "57c86488-8935-4a13-bae0-5ca8783e205d",
    "COACHING": "88169d78-85b4-4fa3-8298-3df020f13a6f",
    "JUST_CHATTING": "2974b0e8-69de-4a13-bae0-5ca8783e205d",
    "MOBILE": "439d8a72-8b8b-4a56-bb32-32c6e5d918ec",
    "Watch Youtube": "d3ae39d2-fd86-41d7-bc38-0b582ce338b5",
    "Play Games": "79bf303a-318b-4815-bd56-7b0b49ae7bff",
    "Virtual Date": "d6b9fc04-bfb2-46df-88eb-6e8c149e34d9"
}

class Services_Database(BasePsqlDTO):
    CHUNK_SIZE = 100  # Number of rows to fetch at a time
    BASE_QUERY = "SELECT * FROM discord_services WHERE profile_score >= 100"

    def __init__(
        self,
        app_choice="ALL",
        user_name=None,
        order_type: Literal["DESC", "ASC"] = "DESC"
    ) -> None:
        self.order_type = order_type
        self.current_offset = 0
        self.current_chunk = []
        self.app_choice = app_choice
        self.user_name = user_name

    async def get_kickers(self) -> List[dict]:
        async with self.get_connection() as conn:
            query = self.BASE_QUERY.replace("*", "discord_id")
            query += " GROUP BY discord_id"
            kicker_ids = await conn.fetch(query)
        return set(
            [int(kicker_id["discord_id"]) for kicker_id in kicker_ids]
        )
    
    async def get_kickers_by_service_title(self, service_title: str) -> List[dict]:
        async with self.get_connection() as conn:
            query = \
                self.BASE_QUERY.replace("*", "discord_id") + " GROUP BY discord_id"
            query_args: tuple = ()
            if service_title.lower() != "all players":
                if "WHERE" in self.BASE_QUERY:
                    query = query.replace("GROUP", "AND service_title = $1 GROUP")
                else:
                    query = query.replace("GROUP", "WHERE service_title = $1 GROUP")
                query_args = (service_title,)
            kicker_ids = await conn.fetch(query, *query_args)
        return set(
            [int(kicker_id["discord_id"]) for kicker_id in kicker_ids]
        )

    async def fetch_chunk(self):
        async with self.get_connection() as conn:
            if self.user_name:
                # Fetch user-specific services first
                query_user = """
                SELECT * FROM discord_services
                WHERE LOWER(profile_username) = LOWER($1)
                LIMIT $2 OFFSET $3;
                """
                user_chunk = await conn.fetch(query_user, self.user_name, self.CHUNK_SIZE, self.current_offset)
                self.current_chunk.extend(user_chunk)

            # Fetch remaining services if user-specific services are less than CHUNK_SIZE
            remaining_chunk_size = self.CHUNK_SIZE - len(self.current_chunk)  # 10
            if remaining_chunk_size > 0:
                default_query = self.BASE_QUERY
                query_args: List = []
                if self.app_choice == "ALL":
                    if self.user_name:
                        default_query += " AND profile_username != $1 LIMIT $2 OFFSET $3;"
                        query_args = [self.user_name, remaining_chunk_size, self.current_offset]
                    else:
                        default_query += " LIMIT $1 OFFSET $2;"
                        query_args = [remaining_chunk_size, self.current_offset]  # LIMIT 10 OFFSET 0
                else:
                    if self.user_name:
                        default_query += " AND service_type_id = $1 AND profile_username != $2 LIMIT $3 OFFSET $4;"
                        query_args = [self.app_choice, self.user_name, remaining_chunk_size, self.current_offset]
                    else:
                        default_query += " AND service_type_id = $1 LIMIT $2 OFFSET $3;"
                        query_args = [self.app_choice, remaining_chunk_size, self.current_offset]
                ordering = "ORDER BY profile_score"
                if self.order_type == "DESC":
                    ordering += " DESC"
                default_query = default_query.replace("LIMIT", f"{ordering} LIMIT")
                # SELECT * FROM discord_services WHERE profile_score >= 100 ORDER BY profile_score LIMIT 10 OFFSET 0
                remaining_chunk = await conn.fetch(default_query, *query_args)
                self.current_chunk.extend(remaining_chunk)

        self.current_offset += self.CHUNK_SIZE
        return self.current_chunk

    async def get_next_service(self):
        if not self.current_chunk:
            chunk = await self.fetch_chunk()
            if not chunk:
                return []
        result = self.current_chunk.pop(0)
        return serialize_profile_data(result)

    async def get_services_by_discordId(self, discordId):
        async with self.get_connection() as conn:
            query = "SELECT * FROM discord_services WHERE discord_id = $1;"
            services = await conn.fetch(query, str(discordId))
        return services
    
    async def get_services_by_username(self, username):
        async with self.get_connection() as conn:
            if self.app_choice == "ALL":
                query = "SELECT * FROM discord_services WHERE profile_username ILIKE $1 LIMIT 1;"
                query_args = [username]
            else:
                query = "SELECT * FROM discord_services WHERE profile_username ILIKE $1 AND service_type_id = $2 LIMIT 1;"
                query_args = [username, APP_CHOICES[self.app_choice]]
            services = await conn.fetch(query, *query_args)
        
        result = serialize_profile_data(services.pop()) if services else None
        return result

    async def get_service_category_name(self, service_type_id):
        async with self.get_connection() as conn:
            query = "SELECT name FROM discord_service_types WHERE id = $1;"
            service_type = await conn.fetchval(query, service_type_id)
        return service_type if service_type else "Unknown"

    async def get_channel_ids(self):
        async with self.get_connection() as conn:
            query = "SELECT channel_id FROM discord_server_channels;"
            records = await conn.fetch(query)
        return records

    async def get_all_active_tags(self):
        default_query = \
            self.BASE_QUERY.replace("*", "service_type_name") + " GROUP BY service_type_name"
        async with self.get_connection() as conn:
            tags = await conn.fetch(default_query)
        return [tag["service_type_name"] for tag in tags]
    
    async def get_managers(self):
        return managers

    async def get_facts(self):
        return facts
    
    async def save_order(self, timestamp: str, order_id: str, user_discord_id: int, kicker_discord_id: int, order_category: str, respond_time: str, service_price: float):
        async with self.get_connection() as conn:
            query = """
            INSERT INTO discord_bot.orders (timestamp, order_id, user_discord_id, order_category, kicker_discord_id, respond_time, service_price)
            VALUES ($1, $2, $3, $4, $5, $6, $7);
            """
            await conn.execute(query, timestamp, order_id, str(user_discord_id), order_category, str(kicker_discord_id), respond_time, service_price)

    async def update_order_kicker_selected(self, order_id: str, kicker_discord_id: int):
        async with self.get_connection() as conn:
            query = """
            UPDATE discord_bot.orders
            SET kicker_selected = TRUE
            WHERE order_id = $1 AND kicker_discord_id = $2;
            """
            await conn.execute(query, order_id, str(kicker_discord_id))

    async def get_kicker_ids_and_score(self):
        async with self.get_connection() as conn:
            query = """
            SELECT discord_id, MAX(profile_score) AS profile_score FROM discord_services
                GROUP BY discord_id
                ORDER BY profile_score DESC;
            """
            services = await conn.fetch(query)
        return services
    
    async def log_to_database(self, discord_id, command_type, server_id):
        async with self.get_connection() as conn:
            if server_id is None:
                query = "INSERT INTO discord_bot.command_logs (discord_id, command_type) VALUES ($1, $2);"
                await conn.execute(query, discord_id, command_type)
            else:
                query = "INSERT INTO discord_bot.command_logs (discord_id, command_type, server_id) VALUES ($1, $2, $3);"
                await conn.execute(query, discord_id, command_type, server_id)
            
    async def save_user_wot_tournament(self, discord_id):
        async with self.get_connection() as conn:
            query = "INSERT INTO discord_bot.discord_users (discord_id) VALUES ($1);"
            await conn.execute(query, discord_id)
    
    async def get_user_ids_wot_tournament(self):
        async with self.get_connection() as conn:
            query = "SELECT discord_id FROM discord_bot.discord_users"
            user_ids = await conn.fetch(query)
        
        return [record['discord_id'] for record in user_ids]