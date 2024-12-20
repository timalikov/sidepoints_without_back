from typing import Literal, Dict, List, Optional, TypeVar, Tuple

import discord
from discord.ui import View

from translate import translations
from bot_instance import get_bot

from models.enums import CouponType
from models.kicker_service import build_service_price
from message_constructors import create_profile_embed

V = TypeVar('V', bound='View', covariant=True)
bot = get_bot()


class CouponDropdownMenu(discord.ui.Select):
    def _build_label_description(self, coupon: Dict) -> str:
        descriptions = {
            CouponType.DISCOUNT: translations["five_dollar_discount"][self.lang],
            CouponType.FREE_ORDER: translations["discount_100"][self.lang],
            CouponType.DISCOUNT_PERCENTAGE: translations["discount_percentage_coupon"][self.lang],
            CouponType.ORDER_VALUE: translations["fixed_price_offer"][self.lang],
        }
        coupon_type = CouponType.by_string_name(coupon["type"])
        description = descriptions[coupon_type]
        if coupon_type == CouponType.DISCOUNT_PERCENTAGE:
            try:
                percent = coupon["params"]["discount"]
            except KeyError:
                percent = 50
            description = descriptions[coupon_type].format(
                percent=percent
            )
        return CouponType.get_value(coupon), description

    def __init__(self, *, coupons: Dict, lang: Literal["en", "ru"]) -> None:
        self.coupons = coupons
        self.lang = lang
        options: List[discord.SelectOption] = []
        for index, coupon in enumerate(coupons):
            label, description = self._build_label_description(coupon)
            option = discord.SelectOption(
                label=label,
                description=description,
                value=index,
                default=index == 0
            )
            options.append(option)
        options.append(discord.SelectOption(
            label="None",
            value=-1
        ))
        super().__init__(placeholder="Select your coupon...", min_values=1, max_values=1, options=options)

    def set_coupon(self) -> Tuple:
        index = int(self.values[0])
        if index == -1:
            coupon = None
        else:
            coupon = self.coupons[index]
        try:
            self.view.coupon = coupon
        except AttributeError:
            setattr(self.view, "coupon", coupon)
        return index, coupon

    @property
    def view(self) -> Optional[V]:
        """Optional[:class:`View`]: The underlying view for this item."""
        return self._view
    
    @view.setter
    def view(self, view) -> None:
        if not isinstance(view, View):
            raise ValueError("Attribute view must be View!")
        self._view = view
        self.set_coupon()

    async def callback(self, interaction: discord.Interaction):
        index, coupon = self.set_coupon()
        for option in self.options:
            option.default = (str(option.value) == str(index))
        embed = create_profile_embed(
            profile_data=self.view.service,
            coupon=coupon,
            lang=self.lang
        )
        await interaction.response.edit_message(view=self.view, embed=embed)
