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
        lang: Literal["ru", "en"] = "en",
    ):
        super().__init__(label="Go", style=discord.ButtonStyle.primary, custom_id="payment", emoji="🎮")
        self.discord_server_id = discord_server_id
        self.lang = lang
        self.pressed_kickers = []
        self._view_variables = ["service"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if not self.discord_server_id:
            self.discord_server_id = interaction.guild_id if interaction.guild_id else int(MAIN_GUILD_ID)
        payment_status_code = await send_payment(
            user=interaction.user,
            target_service=self.view.service,
            discord_server_id=self.discord_server_id
        )
        balance = await get_usdt_balance_by_discord_user(interaction.user)
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
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )
        self.disabled = True
