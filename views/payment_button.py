import discord
from typing import Literal, Dict

from translate import translations

from config import MAIN_GUILD_ID
from models.payment import send_payment, get_usdt_balance_by_discord_user
from models.enums import PaymentStatusCodes
from services.messages.interaction import send_interaction_message
from views.top_up_view import TopUpView


class PaymentButton(discord.ui.Button):
    def __init__(
        self,
        service: Dict,
        discord_server_id: int,
        lang: Literal["ru", "en"] = "en",
    ):
        super().__init__(label="Go", style=discord.ButtonStyle.green, custom_id="payment")
        self.service = service
        self.discord_server_id = discord_server_id
        self.lang = lang
        self.pressed_kickers = []

    async def callback(self, interaction: discord.Interaction):
        return
        await interaction.response.defer(ephemeral=True, thinking=True)
        if interaction.user in self.pressed_kickers:
            return await send_interaction_message(
                interaction=interaction,
                message=translations['already_pressed'][self.lang]
            )
        self.pressed_kickers.append(interaction.user)
        discordServerId = interaction.guild.id if interaction.guild else MAIN_GUILD_ID
        payment_status_code = await send_payment(
            user=interaction.user,
            target_service=self.service,
            discord_server_id=discordServerId
        )
        balance = await get_usdt_balance_by_discord_user(interaction.user)
        messages_kwargs = {
            PaymentStatusCodes.SUCCESS: {
                "embed": discord.Embed(
                    description=translations["success_payment"][self.lang].format(
                        amount=self.service["service_price"], balance=balance
                    ),
                    title="Success",
                    colour=discord.Colour.green()
                )
            },
            PaymentStatusCodes.NOT_ENOUGH_MONEY: {
                "embed": discord.Embed(
                    description=translations["not_enough_money_payment"][self.lang],
                    title="Not enough money",
                    colour=discord.Colour.gold()
                ),
                "view": TopUpView(
                    amount=float(self.service["service_price"]) - float(balance),
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
