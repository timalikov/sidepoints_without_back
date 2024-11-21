from typing import Coroutine, Any, Literal
import discord

from views.buttons.chat_button import ChatButton
from views.buttons.boost_button import BoostButton
from views.buttons.reject_button import RejectButton
from views.buttons.send_accept_reject_button import SendAcceptRejectButton
from views.base_view import BaseView

from bot_instance import get_bot

bot = get_bot()


class OrderPlayView(BaseView):
    
    def __init__(
        self,
        *,
        customer: discord.User,
        main_interaction: discord.Interaction,
        service: dict,
        kicker_id: int,
        guild_id: int,
        order_view: Any,
        lang: Literal["en", "ru"]

    ) -> None:
        super().__init__(timeout=60 * 5)
        self.main_interaction = main_interaction
        self.service = service
        self.service_id = service['service_id']
        self.kicker_id = kicker_id
        self.customer = customer
        self.already_pressed = False
        self.discord_service_id = guild_id
        self.order_view = order_view
        self.boost_amount = None
        self.lang = lang
        self.add_buttons()

    def add_buttons(self) -> None:
        accept_reject_button = SendAcceptRejectButton(
            discord_server_id=self.discord_service_id,
            lang=self.lang
        )
        reject_button = RejectButton(lang=self.lang)
        boost_button = BoostButton(show_dropdown=False, lang=self.lang)
        chat_button = ChatButton(lang=self.lang)
        self.add_item(accept_reject_button)
        self.add_item(reject_button)
        self.add_item(chat_button)
        self.add_item(boost_button)

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        await self.disable_all_buttons()
