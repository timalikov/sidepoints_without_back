from typing import Literal
import os
from dotenv import load_dotenv


from bot_instance import get_bot
from config import APP_CHOICES

from message_constructors import create_boost_embed
from views.buttons.boost_button import BoostButton
from views.base_view import BaseView
from views.buttons.next_button import NextButton
from database.dto.psql_services import Services_Database

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES


class BoostView(BaseView):
    def __init__(
        self,
        amount: float,
        user_name: str = None,
        user_id: int = None,
        lang: Literal["ru", "en"] = "en"
    ) -> None:
        super().__init__(timeout=None)
        self.user_name = user_name
        self.user_id = user_id
        self.no_user = False
        self.service = None
        self.index = 0
        self.profile_embed = None
        self.boost_amount = amount
        self.lang = lang
        if user_id:
            self.service_db = Services_Database()
            self.service_index = 0
        else:
            self.service_db = Services_Database(user_name=self.user_name)

    async def initialize(self):
        if self.user_id:
            self.services = await self.service_db.get_services_by_discordId(self.user_id)
            self.service = self.services[self.service_index] if self.services else None
        else:
            self.service = await self.service_db.get_next_service()
        if self.service:
            self.profile_embed = create_boost_embed(self.service, lang=self.lang, amount=self.boost_amount)
        else:
            self.no_user = True
        self.add_buttons()

    async def set_service(self):
        """
        Helper function to set the service and create the embed.
        """
        if self.user_id:
            self.service_index = (self.service_index + 1) % len(self.services)
            self.service = self.services[self.service_index]
        else:
            self.service = await self.service_db.get_next_service()

        self.profile_embed = create_boost_embed(self.service, lang=self.lang, amount=self.boost_amount)

    def add_buttons(self) -> None:
        next_button = NextButton(is_list=True, lang=self.lang)
        boost_button = BoostButton(show_dropdown=False, lang=self.lang)
        self.add_item(boost_button)
        self.add_item(next_button)
