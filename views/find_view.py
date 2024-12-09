from typing import Literal

import os
from dotenv import load_dotenv

from services.kicker_sort_service import KickerSortingService
from message_constructors import create_profile_embed
from bot_instance import get_bot
from views.buttons.boost_button import BoostButton
from views.base_view import BaseView
from views.buttons.chat_button import ChatButton
from database.dto.psql_services import Services_Database
from views.buttons.send_accept_reject_button import SendAcceptRejectButton

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))


class FindView(BaseView):
    @classmethod
    async def create(
        cls,
        user_choice = "ALL",
        username: str = None,
        user_id: int = None,
        guild_id: int = main_guild_id,
        lang: Literal["ru", "en"] = "en"
    ):
        services_db = Services_Database(app_choice=user_choice)
        instance = cls(None, services_db, lang=lang)
        
        instance.services_db = services_db
        instance.kicker_sorting_service = KickerSortingService(services_db)
        instance.guild_id = guild_id

        if username:
            service = await services_db.get_services_by_username(username)
        elif user_id:
            services = await services_db.get_services_by_discordId(user_id)
            service = services[0] if services else None
        else:
            service = await instance.kicker_sorting_service.fetch_first_service()

        if service:
            instance.set_service(service)
        else:
            instance.no_user = True
        instance.add_buttons()
        return instance 
    
    def __init__(
        self,
        service: dict = None,
        services_db: Services_Database = None,
        guild_id: int = main_guild_id,
        lang: Literal["ru", "en"] = "en"
    ) -> None:
        super().__init__(timeout=None)
        self.service = service
        self.services_db = services_db
        self.guild_id = guild_id
        self.no_user = False  
        self.profile_embed = None
        self.kicker_sorting_service = None
        self.lang = lang

    def set_service(self, service):
        """
        Helper function to set the service and create the embed.
        """
        self.service = service
        self.profile_embed = create_profile_embed(service, lang=self.lang)
        self.no_user = False

    def add_buttons(self) -> None:
        payment_button = SendAcceptRejectButton(
            discord_server_id=self.guild_id,
            lang=self.lang
        )
        chat_button = ChatButton(lang=self.lang)
        boost_button = BoostButton(show_dropdown=True, lang=self.lang)
        self.add_item(payment_button)
        self.add_item(chat_button)
        self.add_item(boost_button)
