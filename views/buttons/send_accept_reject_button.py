import discord
from typing import Literal

from translate import translations

from bot_instance import get_bot
from services.messages.interaction import send_interaction_message
from services.logger.client import CustomLogger
from models.payment import (
    check_user_wallet,
    get_usdt_balance_by_discord_user
)
from models.enums import PaymentStatusCode
from models.kicker_service import build_service_price
from views.buttons.base_button import BaseButton
from views.access_reject import AccessRejectView
from views.dropdown.top_up_dropdown import TopUpDropdownMenu

bot = get_bot()
logger = CustomLogger


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
        self._view_variables = ["service", "coupon"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        service_price = build_service_price(self.view.service, self.view.coupon)
        status = await check_user_wallet(
            user=interaction.user,
            amount=service_price
        )
        if status == PaymentStatusCode.NOT_ENOUGH_MONEY:
            balance = await get_usdt_balance_by_discord_user(
                user=interaction.user
            )
            top_up_dropdown = TopUpDropdownMenu(lang=self.lang)
            top_up_dropdown_view = discord.ui.View(timeout=None)
            top_up_dropdown_view.add_item(top_up_dropdown)
            await send_interaction_message(
                interaction=interaction,
                embed=discord.Embed(
                    description=translations["not_enough_money_payment"][self.lang],
                    title="🔴 Not enough balance",
                    colour=discord.Colour.gold()
                ),
                view=top_up_dropdown_view
            )
            return
        try:
            kicker_id = int(self.view.service["discord_id"])
            kicker = bot.get_user(kicker_id)
        except (ValueError, TypeError) as e:
            await logger.error_discord(f"ERROR IN SEND ACCEPT REJECT BUTTON: {e}")
            await send_interaction_message(
                interaction=interaction,
                embed=discord.Embed(
                    title="🔴 Error",
                    description=translations["server_error_payment"][self.lang],
                    color=discord.Color.red()
                )
            )
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
        coupon = getattr(self.view, "coupon", None)
        view = AccessRejectView(
            kicker=kicker,
            customer=interaction.user,
            service=self.view.service,
            discord_server_id=self.discord_server_id,
            coupon=coupon,
            lang=self.lang,
            collector=self.view.collector
        )
        service = self.view.service
        kicker_embed = discord.Embed(
            colour=discord.Colour.dark_blue(),
            title=translations["service_purchased_title"][self.lang],
            description=translations["service_details"][self.lang].format(
                customer_name=interaction.user.name,
                customer_id=interaction.user.id,
                service_name=service['tag'] if service else 'Not found',
                service_price=service['service_price'] if service else 'Not found',
            )       
        )
        view.message = await kicker.send(embed=kicker_embed, view=view)
        if coupon:
            message_embed_description = translations["order_sent_with_coupon"][self.lang].format(
                kicker_name=kicker.name,
                discount=float(self.view.service["service_price"]) - service_price,
                original_price=self.view.service["service_price"],
                new_price=service_price
            )
        else:
            message_embed_description = translations["order_sent"][self.lang].format(kicker_name=kicker.name)
        message_embed = discord.Embed(
            colour=discord.Colour.dark_blue(),
            title=translations["order_in_process"][self.lang],
            description=message_embed_description
        )
        
        if interaction.guild:
            await interaction.user.send(embed=message_embed)
        await send_interaction_message(
            interaction=interaction,
            embed=message_embed
        )
