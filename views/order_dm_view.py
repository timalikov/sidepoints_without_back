from typing import Literal
from button_constructors import StopDispatchingButton
from config import YELLOW_LOGO_COLOR
import discord
from views.top_up_view import TopUpDropdownMenu

class OrderDMView(discord.ui.View):

    def __init__(
        self, 
        *,
        order_view: discord.ui.View,
        lang: Literal["en", "ru"] = "en",
    ):
        super().__init__(timeout=None)
        self.lang = lang
        self.embed_message = self._build_embed_message_points()

        self.add_item(
            TopUpDropdownMenu(lang=lang)
        )
        self.add_item(StopDispatchingButton(order_view=order_view))


    def _build_embed_message_points(self):
        embed = discord.Embed(
            title="🎟Thanks for placing an order",
            description="While you wait for the order dispatch, please make sure you have 💰sufficient balance💰 on your account.\nYou may 💶top up💶 using the following methods.",
            color=discord.Color.from_rgb(*YELLOW_LOGO_COLOR)
        )
       
        return embed