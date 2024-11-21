from typing import Coroutine, List, Any, Literal
from datetime import datetime
import uuid
import discord

from database.dto.psql_services import Services_Database
from views.buttons.order_go_button import OrderGoButton
from views.base_view import BaseView
from views.buttons.count_button import CountButton
from services.messages.order import OrderMessageManager
from translate import translations

from bot_instance import get_bot

bot = get_bot()


class OrderView(BaseView):
    """
    Like a Yandex taxi!

    Kickers will press the access button
    and customer get a message.
    """

    def __init__(
        self,
        *,
        customer: discord.User,
        guild_id: int,
        order_id: uuid.UUID = None,
        extra_text: str = "",
        lang: Literal["en", "ru"] = "en",
        services_db: Services_Database = None,
        go_command: bool = False
    ):
        super().__init__(timeout=15 * 60)
        self.customer: discord.User = customer
        self.pressed_kickers: List[discord.User] = []
        self.is_pressed = False
        self.services_db = services_db
        self.go_command = go_command
        self.messages = []  # for drop button after timeout
        self.created_at = datetime.now()
        self.guild_id = int(guild_id) if guild_id else None
        self.lang = lang
        self.webapp_order = False
        if order_id:
            self.order_id = order_id
            self.webapp_order = True
        else:
            self.order_id = str(uuid.uuid4())
        self.boost_amount = None
        self.message_manager = OrderMessageManager(
            customer=self.customer,
            guild_id=self.guild_id,
            services_db=self.services_db,
            extra_text=extra_text,
            view=self
        )
        self.add_buttons()

    def add_buttons(self) -> None:
        self.add_item(OrderGoButton(lang=self.lang))
        self.add_item(CountButton(lang=self.lang))

    async def on_timeout(self, stop_button_pressed: bool = False) -> Coroutine[Any, Any, None]:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        for message_instance in self.messages:
            await message_instance.edit(view=self)
        if stop_button_pressed:
            stopped_message_embed = discord.Embed(
                title=translations['order_terminated'][self.lang],
                description=translations['you_requested_stop_summon'][self.lang],
                color=discord.Color.red()
            )
            await self.customer.send(embed=stopped_message_embed, view=None)
            return
        if not self.is_pressed:
            timeout_message_embed = discord.Embed(
                title=translations['order_terminated'][self.lang],
                description=translations['timeout_message'][self.lang],
                color=discord.Color.red()
            )
            await self.customer.send(embed=timeout_message_embed, view=None)
