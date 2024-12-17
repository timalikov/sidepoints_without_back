from typing import Literal, Dict, List

import discord

from translate import translations
from bot_instance import get_bot

from models.enums import CouponType
from models.kicker_service import build_service_price
from message_constructors import create_profile_embed


bot = get_bot()


class CouponDropdownMenu(discord.ui.Select):
    def __init__(self, *, coupons: Dict, lang: Literal["en", "ru"]) -> None:
        self.coupons = coupons
        self.lang = lang
        descriptions = {
            CouponType.DISCOUNT: translations["five_dollar_discount"][self.lang],
            CouponType.FREE_ORDER: translations["discount_100"][self.lang],
            CouponType.DISCOUNT_PERCENTAGE: translations["half_price_offer"][self.lang],
            CouponType.ORDER_VALUE: translations["fixed_price_offer"][self.lang],
        }
        options: List[discord.SelectOption] = []
        for index, coupon in enumerate(coupons):
            coupon_type = CouponType.by_string_name(coupon["type"])
            option = discord.SelectOption(
                label=coupon_type.value,
                description=descriptions[coupon_type],
                value=index
            )
            options.append(option)
        super().__init__(placeholder="Select your coupon...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])
        coupon = self.coupons[index]
        try:
            self.view.coupon = coupon
        except AttributeError:
            setattr(self.view, "coupon", coupon)
        for option in self.options:
            option.default = (str(option.value) == str(index))
        embed = create_profile_embed(
            profile_data=self.view.service,
            coupon=coupon,
            lang=self.lang
        )
        await interaction.response.edit_message(view=self.view, embed=embed)
