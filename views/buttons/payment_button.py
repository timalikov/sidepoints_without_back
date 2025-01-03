import discord
from typing import Literal

from translate import translations

from config import MAIN_GUILD_ID
from bot_instance import get_bot
from models.payment import send_payment, get_usdt_balance_by_discord_user
from models.enums import PaymentStatusCode, CouponType
from models.kicker_service import build_service_price
from services.messages.interaction import send_interaction_message
from views.buttons.base_button import BaseButton
from views.dropdown.top_up_dropdown import TopUpDropdownMenu
from services.cache.client import custom_cache
from logging import getLogger

bot = get_bot()
logger = getLogger("")


class PaymentButton(BaseButton):
    def __init__(
        self,
        discord_server_id: int = None,
        customer: discord.User = None,
        lang: Literal["ru", "en"] = "en",
    ):
        super().__init__(label="Go", style=discord.ButtonStyle.primary, custom_id="payment", emoji="🎮")
        self.discord_server_id = discord_server_id
        self.lang = lang
        self.pressed_kickers = []
        self.customer = customer
        self._view_variables = ["service"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            await self.view.stop_refund_manager()
            await self.view.disable_all_buttons()
        except Exception:
            ...
        if self.customer:
            await send_interaction_message(
                interaction=interaction,
                embed=discord.Embed(
                    colour=discord.Colour.green(),
                    title=translations["order_in_process"][self.lang],
                    description=translations["session_accepted_message"][self.lang].format(
                        discord_user=self.customer.name
                    )
                )
            )
        if not self.discord_server_id:
            self.discord_server_id = interaction.guild_id if interaction.guild_id else int(MAIN_GUILD_ID)
        user = self.customer if self.customer else interaction.user
        service_price = build_service_price(self.view.service, self.view.coupon)
        payment_status_code, purchase_id = await send_payment(
            user=user,
            target_service=self.view.service,
            discord_server_id=self.discord_server_id,
            coupon=self.view.coupon
        )
        balance = await get_usdt_balance_by_discord_user(user)
        coupon = getattr(self.view, "coupon", None)
        top_up_dropdown = TopUpDropdownMenu(lang=self.lang)
        top_up_dropdown_view = discord.ui.View(timeout=None)
        top_up_dropdown_view.add_item(top_up_dropdown)
        messages_kwargs = {
            PaymentStatusCode.SUCCESS: {
                "embed": discord.Embed(
                    description=(
                        translations["success_payment"][self.lang].format(
                            amount=service_price, balance=balance
                        )
                        if not coupon
                        else translations["success_payment_with_coupon"][self.lang].format(
                            amount=service_price,
                            balance=balance,
                            coupon_type=CouponType.get_value(coupon),
                            original_price=self.view.service["service_price"],
                            discount=float(self.view.service["service_price"]) - service_price,
                            new_price=service_price
                        )
                    ),
                    title="✅ Payment Success",
                    colour=discord.Colour.green()
                )
            },
            PaymentStatusCode.NOT_ENOUGH_MONEY: {
                "embed": discord.Embed(
                    description=translations["not_enough_money_payment"][self.lang],
                    title="🔴 Not enough balance",
                    colour=discord.Colour.gold()
                ),
                "view": top_up_dropdown_view
            },
            PaymentStatusCode.SERVER_PROBLEM: {
                "embed": discord.Embed(
                    description=translations["server_error_payment"][self.lang],
                    colour=discord.Colour.red()
                )
            },
        }
        message_kwargs = messages_kwargs.get(payment_status_code, translations["server_error_payment"][self.lang])
        if self.customer:
            await user.send(**message_kwargs)
        else:
            await send_interaction_message(
                interaction=interaction,
                **message_kwargs
            )

        if payment_status_code == PaymentStatusCode.SUCCESS:
            custom_cache.set_purchase_id(purchase_id)
            order_view = self.view.collector.get_view(name="OrderView")
            if order_view:
                order_view.is_success_payment = True
                await order_view.on_timeout()
            from services.messages.base import send_confirm_order_message
            try:
                kicker: discord.User = bot.get_user(int(self.view.service["discord_id"]))
            except (ValueError, TypeError) as e:
                logger.error(f"Error getting kicker: {e}")
                return
            await send_confirm_order_message(
                customer=user,
                kicker=kicker,
                kicker_username=self.view.service["discord_username"],
                service_name=self.view.service["service_title"],
                purchase_id=purchase_id,
                discord_server_id=int(self.discord_server_id),
            )

        self.disabled = True
        try:
            self.view.already_pressed = True
        except AttributeError:
            pass
