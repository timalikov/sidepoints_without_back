import discord
from typing import Literal

from translate import translations

from bot_instance import get_bot
from services.messages.interaction import send_interaction_message
from models.payment import (
    check_user_wallet,
    get_usdt_balance_by_discord_user
)
from models.enums import PaymentStatusCodes
from views.buttons.base_button import BaseButton
from views.access_reject import AccessRejectView
from views.top_up_view import TopUpView

bot = get_bot()


class SendAcceptRejectButton(BaseButton):
    def __init__(
        self,
        discord_server_id: int = None,
        lang: Literal["ru", "en"] = "en",
    ):
        super().__init__(
            label="Go",
            style=discord.ButtonStyle.primary,
            custom_id="send_accept_reject",
            emoji="🎮"
        )
        self.discord_server_id = discord_server_id
        self.lang = lang
        self._view_variables = ["service"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        status = await check_user_wallet(
            user=interaction.user,
            amount=int(self.view.service["service_price"])
        )
        if status == PaymentStatusCodes.NOT_ENOUGH_MONEY:
            balance = await get_usdt_balance_by_discord_user(
                user=interaction.user
            )
            await send_interaction_message(
                interaction=interaction,
                embed=discord.Embed(
                    description=translations["not_enough_money_payment"][self.lang],
                    title="🔴 Not enough balance",
                    colour=discord.Colour.gold()
                ),
                view=TopUpView(
                    amount=float(self.view.service["service_price"]) - float(balance),
                    guild=bot.get_guild(int(self.discord_server_id)),
                    lang=self.lang
                )
            )
            return
        try:
            kicker_id = int(self.view.service["discord_id"])
            kicker = bot.get_user(kicker_id)
        except (ValueError, TypeError) as e:
            print(f"ERROR IN SEND ACCEPT REJECT BUTTON: {e}")
            return
        if not kicker:
            error_embed = discord.Embed(
                colour=discord.Colour.red(),
                title="Oops...",
                description="Kicker not found..." 
            )
            await send_interaction_message(
                interaction=interaction,
                embed=error_embed
            )
            return
        view = AccessRejectView(
            kicker=kicker,
            customer=interaction.user,
            service=self.view.service,
            discord_server_id=self.discord_server_id,
            lang=self.lang
        )
        service = self.view.service
        message_embed = discord.Embed(
            colour=discord.Colour.dark_blue(),
            title=translations["service_purchased_title"][self.lang],
            description=translations["service_details"][self.lang].format(
                service_name=service['tag'] if service else 'Not found',
                service_price=service['service_price'] if service else 'Not found'
            )       
        )
        message = await kicker.send(embed=message_embed, view=view)
        view.message = message
        await send_interaction_message(
            interaction=interaction,
            embed=discord.Embed(
                colour=discord.Colour.dark_blue(),
                title=translations["order_in_process"][self.lang],
                description=translations["order_sent"][self.lang].format(kicker_name=kicker.name)
            )
        )
