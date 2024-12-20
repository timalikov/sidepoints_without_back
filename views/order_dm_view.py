from typing import Literal, Union
from decimal import Decimal

import discord

from config import YELLOW_LOGO_COLOR
from translate import translations

from views.dropdown.top_up_dropdown import TopUpDropdownMenu
from views.base_view import BaseView
from views.buttons.stop_dispatching_button import StopDispatchingButton
from services.view_collector import ViewCollector

class OrderDMView(BaseView):

    def __init__(
        self, 
        *,
        order_view: discord.ui.View,
        balance: Union[int, Decimal, Literal["Failed to connect to BNB Smart Chain"]],
        lang: Literal["en", "ru"] = "en",
        collector: ViewCollector = None
    ):
        super().__init__(timeout=None, collector=collector)
        self.balance = balance
        self.lang = lang
        self.embed_message = self._build_embed_message_points()

        self.add_item(TopUpDropdownMenu(lang=lang))
        self.add_item(StopDispatchingButton(order_view=order_view, order_dm_view=self))

    def _build_embed_message_points(self):
        embed = discord.Embed(
            title=translations["thanks_for_placing_order"][self.lang],
            description=translations["thanks_for_placing_order_description"][self.lang].format(balance=self.balance),    
            color=discord.Color.from_rgb(*YELLOW_LOGO_COLOR)
        )
        embed.set_image(url="https://discord-photos.s3.eu-central-1.amazonaws.com/sidekick-back-media/discord_bot/Order-complete.png")
        return embed