from typing import Literal, Dict

import discord

from config import (
    BOOST_KICKER_CATEGORY_NAME,
    BOOST_KICKER_CHANNEL_NAME,
    MAIN_GUILD_ID
)
from translate import translations
from bot_instance import get_bot

from services.messages.interaction import send_interaction_message
from views.top_up_view import TopUpView
from models.public_channel import get_or_create_channel_by_category_and_name
from models.enums import PaymentStatusCodes
from models.payment import send_boost

bot = get_bot()


class BoostDropdownMenu(discord.ui.Select):
    def __init__(
        self,
        *,
        target_service: Dict,
        need_send_boost: bool = True,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        _amounts: Dict[int, str] = {
            10: "Heart - 10 USDT",
            50: "Sunglasses - 50 USDT",
            100: "Carnival - 100 USDT",
            # 100: "Air Balloon - 100 USDT",
            200: "Boost rocket - 200 USDT",
            # 200: "Sport car - 200 USDT",
        }
        options = [
            discord.SelectOption(label=str(amount), description=text)
            for amount, text in _amounts.items()
        ]
        self.need_send_boost = need_send_boost
        self.target_service = target_service
        self.lang = lang
        super().__init__(placeholder="Select amount for boost...", min_values=1, max_values=1, options=options)

    async def _with_payment(self, interaction: discord.Interaction, amount: float) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        message_kwargs = await BoostDropdownMenu.send_boost_and_get_message(
            user=interaction.user,
            target_service=self.target_service,
            amount=amount,
            guild=interaction.guild,
            lang=self.lang
        )
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )

    async def _without_payment(self, interaction: discord.Interaction, amount: float) -> None:
        self.view.boost_amount = amount
        for option in self.options:
            option.default = (str(option.label) == str(int(amount)))
        await interaction.response.edit_message(view=self.view)

    async def callback(self, interaction: discord.Interaction):
        amount = float(self.values[0])
        if self.need_send_boost:
            await self._with_payment(interaction, amount)
        else:
            await self._without_payment(interaction, amount)
    
    @staticmethod
    async def send_boost_and_get_message(
        user: discord.User,
        target_service: Dict,
        amount: int,
        guild: discord.Guild,
        lang: Literal["ru", "en"] = "en"
    ) -> Dict:
        payment_status_code: PaymentStatusCodes = await send_boost(
            user=user,
            target_service=target_service,
            amount=amount
        )
        boost_channel = await get_or_create_channel_by_category_and_name(
            category_name=BOOST_KICKER_CATEGORY_NAME,
            channel_name=BOOST_KICKER_CHANNEL_NAME,
            guild=bot.get_guild(MAIN_GUILD_ID)
        )
        messages_kwargs = {
            PaymentStatusCodes.SUCCESS: {
                "embed": discord.Embed(
                    description=translations["public_boost_announcement_message"][lang].format(
                        username=user.name,
                        kickername=target_service["discord_username"],
                        amount=amount,
                        link=boost_channel.jump_url
                    ),
                    title="✅ Payment Success",
                    colour=discord.Colour.green()
                ),
                "ephemeral": False
            },
            PaymentStatusCodes.NOT_ENOUGH_MONEY: {
                "embed": discord.Embed(
                    description=translations["not_enough_money_payment"][lang],
                    title="🔴 Not enough balance",
                    colour=discord.Colour.gold()
                ),
                "view": TopUpView(
                    amount=amount,
                    guild=guild,
                    lang=lang
                ),
                "ephemeral": True
            },
            PaymentStatusCodes.SERVER_PROBLEM: {
                "embed": discord.Embed(
                    description=translations["server_error_payment"][lang],
                    colour=discord.Colour.red()
                ),
                "ephemeral": True
            },
        }
        response = messages_kwargs.get(payment_status_code)
        return response if response else messages_kwargs[PaymentStatusCodes.SERVER_PROBLEM]

