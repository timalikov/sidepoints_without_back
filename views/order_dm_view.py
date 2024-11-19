from decimal import Decimal
from typing import Literal, Union
from button_constructors import StopDispatchingButton
from config import YELLOW_LOGO_COLOR
import discord
from views.dropdown.top_up_dropdown import TopUpDropdownMenu
from translate import translations

class OrderDMView(discord.ui.View):

    def __init__(
        self, 
        *,
        order_view: discord.ui.View,
        balance: Union[int, Decimal, Literal["Failed to connect to BNB Smart Chain"]],
        lang: Literal["en", "ru"] = "en",
    ):
        super().__init__(timeout=None)
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
        return embed