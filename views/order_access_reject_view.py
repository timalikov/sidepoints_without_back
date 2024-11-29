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
        service: dict,
        guild_id: int,
        need_reject_button: bool = True,
        need_boost_button: bool = True,
        need_payment_button: bool = True,
        need_chat_button: bool = True,
        show_boost_dropdown: bool = False,
        lang: Literal["en", "ru"],
        timeout: int = 60 * 60
    ) -> None:
        super().__init__(timeout=timeout)
        self.service = service
        self.service_id = service['service_id']
        self.already_pressed = False
        self.discord_service_id = guild_id
        self.boost_amount = None
        self.lang = lang
        self.need_reject_button = need_reject_button
        self.need_boost_button = need_boost_button
        self.need_payment_button = need_payment_button
        self.need_chat_button = need_chat_button
        self.show_boost_dropdown = show_boost_dropdown
        self.add_buttons()

    def add_buttons(self) -> None:
        if self.need_payment_button:
            accept_reject_button = SendAcceptRejectButton(
                discord_server_id=self.discord_service_id,
                lang=self.lang
            )
            self.add_item(accept_reject_button)
        if self.need_reject_button:
            reject_button = RejectButton(lang=self.lang)
            self.add_item(reject_button )
        if self.need_boost_button:
            boost_button = BoostButton(show_dropdown=self.show_boost_dropdown, lang=self.lang)
            self.add_item(boost_button)
        if self.need_chat_button:
            chat_button = ChatButton(lang=self.lang)
            self.add_item(chat_button)

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        await self.disable_all_buttons()
