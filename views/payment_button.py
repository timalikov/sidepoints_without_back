import discord
from typing import Literal, Dict

from translate import translations

from models.payment import send_payment
from models.enums import PaymentStatusCodes
from services.messages.interaction import send_interaction_message


class PaymentButton(discord.ui.View):
    def __init__(
        self,
        service: Dict,
        discord_server_id: int,
        lang: Literal["ru", "en"] = "en",
    ):
        super().__init__(timeout=None)
        self.service = service
        self.discord_server_id = discord_server_id
        self.lang = lang

    @discord.ui.button(label="Go", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        payment_status_code = await send_payment(
            user=interaction.guild.get_member(930005621728763904),
            target_service=self.service,
            discord_server_id=self.discord_server_id
        )
        messages = {
            PaymentStatusCodes.SUCCESS: translations["success_payment"][self.lang],
            PaymentStatusCodes.NOT_ENOUGH_MONEY: translations["not_enough_money_payment"][self.lang],
            PaymentStatusCodes.SERVER_PROBLEM: translations["server_error_payment"][self.lang],
        }
        message = messages.get(payment_status_code, translations["server_error_payment"][self.lang])
        await send_interaction_message(
            interaction=interaction,
            message=message
        )
        button.disabled = True
