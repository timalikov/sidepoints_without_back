import discord
from typing import Literal

from translate import translations

from config import MAIN_GUILD_ID
from bot_instance import get_bot
from models.payment import send_payment, get_usdt_balance_by_discord_user
from models.enums import PaymentStatusCodes
from services.messages.interaction import send_interaction_message
from views.buttons.base_button import BaseButton
from views.top_up_view import TopUpView

bot = get_bot()


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
        self._view_variables = ["service", "kicker"]

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
        payment_status_code, purchase_id = await send_payment(
            user=user,
            target_service=self.view.service,
            discord_server_id=self.discord_server_id
        )
        balance = await get_usdt_balance_by_discord_user(user)
        try:
            guild: discord.Guild = bot.get_guild(int(self.discord_server_id))
        except ValueError:
            guild: discord.Guild = None
        messages_kwargs = {
            PaymentStatusCodes.SUCCESS: {
                "embed": discord.Embed(
                    description=translations["success_payment"][self.lang].format(
                        amount=self.view.service["service_price"], balance=balance
                    ),
                    title="✅ Payment Success",
                    colour=discord.Colour.green()
                )
            },
            PaymentStatusCodes.NOT_ENOUGH_MONEY: {
                "embed": discord.Embed(
                    description=translations["not_enough_money_payment"][self.lang],
                    title="🔴 Not enough balance",
                    colour=discord.Colour.gold()
                ),
                "view": TopUpView(
                    amount=float(self.view.service["service_price"]) - float(balance),
                    guild=guild,
                    lang=self.lang
                )
            },
            PaymentStatusCodes.SERVER_PROBLEM: {
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

        if payment_status_code == PaymentStatusCodes.SUCCESS:
            from services.messages.base import send_confirm_order_message
            kicker: discord.User = bot.get_user(int(self.view.service["discord_id"]))
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
