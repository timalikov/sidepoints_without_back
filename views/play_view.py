from typing import Literal

from discord.ui import View

import os
from dotenv import load_dotenv

from services.view_collector import ViewCollector
from services.kicker_sort_service import KickerSortingService
from message_constructors import create_profile_embed
from bot_instance import get_bot
from views.buttons.boost_button import BoostButton
from views.buttons.next_button import NextButton
from views.buttons.share_button import ShareButton
from views.buttons.chat_button import ChatButton
from views.buttons.send_accept_reject_button import SendAcceptRejectButton
from views.impls.coupon_interface import CouponInterface
from views.base_view import BaseView
from database.dto.psql_services import Services_Database


bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))


class PlayView(BaseView, CouponInterface):
    @classmethod
    async def create(
        cls,
        user_choice = "ALL",
        username = None,
        guild_id: int = main_guild_id,
        lang: Literal["ru", "en"] = "en",
        collector: ViewCollector = None
    ):
        services_db = Services_Database(app_choice=user_choice)
        instance = cls(None, services_db, discord_service_id=guild_id, lang=lang, collector=collector)
        
        instance.services_db = services_db
        instance.kicker_sorting_service = KickerSortingService(services_db)

        if username:
            service = await services_db.get_services_by_username(username)
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
        discord_service_id: int = main_guild_id,
        lang: Literal["ru", "en"] = "en",
        collector: ViewCollector = None
    ) -> None:
        super().__init__(timeout=None, collector=collector)
        self.service = service
        self.services_db = services_db
        self.no_user = False  
        self.profile_embed = None
        self.kicker_sorting_service = None
        self.discord_service_id = discord_service_id
        self.lang = lang

    def add_buttons(self) -> None:
        payment_button = SendAcceptRejectButton(
            discord_server_id=self.discord_service_id,
            lang=self.lang
        )
        next_button = NextButton(
            kicker_sorting_service=self.kicker_sorting_service,
            lang=self.lang
        )
        share_button = ShareButton(lang=self.lang)
        boost_button = BoostButton(show_dropdown=True, lang=self.lang)
        chat_button = ChatButton(lang=self.lang)
        self.add_item(payment_button)
        self.add_item(next_button)
        self.add_item(share_button)
        self.add_item(chat_button)
        self.add_item(boost_button)

    def set_service(self, service):
        """
        Helper function to set the service and create the embed.
        """
        self.service = service
        self.profile_embed = create_profile_embed(service, lang=self.lang)
        self.no_user = False  
