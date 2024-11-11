from database.dto.psql_services import Services_Database
from bot_instance import get_bot
import discord
from config import MAIN_GUILD_ID

bot = get_bot()

class KickerSortingService:
    def __init__(self, services_db: Services_Database):
        self.services_db = services_db
        self.sorted_kickers = []
        self.current_kicker_index = 0

    async def fetch_first_service(self):
        all_kickers = await self.services_db.get_kicker_ids_and_score()

        if not all_kickers:
            return None  
        
        self.sorted_kickers = await self.sort_kickers(all_kickers)
        self.current_kicker_index = 0
        return await self.get_next_valid_service()

    async def get_next_valid_service(self):
        while self.current_kicker_index < len(self.sorted_kickers):
            kicker = self.sorted_kickers[self.current_kicker_index]
            self.current_kicker_index += 1

            services = await self.services_db.get_services_by_discordId(kicker['discord_id'])
            if services:
                service = dict(services[0])  
                service["service_category_name"] = service["tag"]
                return service
        return None
    
    async def is_user_online(self, user_id):
        main_guild = bot.get_guild(MAIN_GUILD_ID)
        if main_guild is None:
            return False
        try:
            member = main_guild.get_member(int(user_id))
        except ValueError as e:
            print(f"IS USER ONLINE ERROR: {e}")
            member = None
        return member is not None and member.status == discord.Status.online

    async def sort_kickers(self, all_kickers):
        """
        Fetch all kickers and sort them by:
        1. Online kickers with profile_score >= 100.
        2. Online kickers with profile_score < 100.
        3. Offline kickers, sorted by profile_score.
        """

        online_high_score = []
        offline_high_score = []
        online = []
        offline = []

        for kicker in all_kickers:
            try:
                user_id = kicker['discord_id']
                score = kicker['profile_score']

                is_online = await self.is_user_online(user_id)

                if score >= 100:
                    if is_online:
                        online_high_score.append(kicker)
                    else:
                        offline_high_score.append(kicker)
                else:
                    if is_online:
                        online.append(kicker)
                    else:
                        offline.append(kicker)
            except:
                continue

        return online_high_score + offline_high_score + online + offline
