from typing import Literal, List, Dict
import os
from dotenv import load_dotenv

import discord
from discord.ui import View

from bot_instance import get_bot
from config import APP_CHOICES, FORUM_NAME
from translate import translations

from database.dto.sql_forum_posted import ForumUserPostDatabase
from message_constructors import create_boost_embed
from services.messages.interaction import send_interaction_message
from models.payment import send_boost
from models.forum import find_forum
from models.enums import PaymentStatusCodes
from views.top_up_view import TopUpView
from database.dto.psql_services import Services_Database

bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES


class BoostView(View):
    def __init__(self, user_name, amount: float, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.user_name = user_name
        self.no_user = False
        self.service_db = Services_Database(user_name=self.user_name)
        self.user_data = None
        self.index = 0
        self.profile_embed = None
        self.amount = amount
        self.lang = lang

    async def initialize(self):
        self.user_data = await self.service_db.get_next_service()
        if self.user_data:
            self.profile_embed = create_boost_embed(self.user_data, lang=self.lang, amount=self.amount)
        else:
            self.no_user = True

    @staticmethod
    async def _send_boost_and_get_message(
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
        messages_kwargs = {
            PaymentStatusCodes.SUCCESS: {
                "embed": discord.Embed(
                    description=translations["public_boost_announcement_message"][lang].format(
                        username=user.name,
                        kickername=target_service["discord_username"],
                        amount=amount
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
                "ephemeral": False
            },
            PaymentStatusCodes.SERVER_PROBLEM: {
                "embed": discord.Embed(
                    description=translations["server_error_payment"][lang],
                    colour=discord.Colour.red()
                ),
                "ephemeral": False
            },
        }
        response = messages_kwargs.get(payment_status_code)
        return response if response else messages_kwargs[PaymentStatusCodes.SERVER_PROBLEM]

    @discord.ui.button(label="Boost", style=discord.ButtonStyle.success, custom_id="boost")
    async def edit_service(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "boost", 
            interaction.guild.id if interaction.guild else None
        )
        message_kwargs = await BoostView._send_boost_and_get_message(
            user=interaction.user,
            target_service=self.user_data,
            amount=self.amount,
            guild=interaction.guild if interaction.guild else bot.get_guild(main_guild_id),
            lang=self.lang
        )
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )
        button.disabled = True

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_kicker")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "next_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        self.user_data = await self.service_db.get_next_service()

        self.profile_embed = create_boost_embed(self.user_data, lang=self.lang, amount=self.amount)
        await interaction.edit_original_response(embed=self.profile_embed, view=self)


class BoostDropdownMenu(discord.ui.Select):
    def __init__(self, *, target_service: Dict, lang: Literal["en", "ru"] = "en"):
        _amounts: Dict[int, str] = {
            10: "Heart - 10 USDT",
            50: "Sunglasses - 50 USDT",
            100: "Carnival - 100 USDT",
            100: "Air Balloon - 100 USDT",
            200: "Boost rocket - 200 USDT",
            200: "Sport car - 200 USDT",
        }
        options = [
            discord.SelectOption(label=str(amount), description=text)
            for amount, text in _amounts.items()
        ]
        self.target_service = target_service
        self.lang = lang
        super().__init__(placeholder="Select amount...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        message_kwargs: Dict = await BoostView._send_boost_and_get_message(
            user=interaction.user,
            target_service=self.target_service,
            amount=float(self.values[0]),
            guild=interaction.guild if interaction.guild else bot.get_guild(main_guild_id),
            lang=self.lang
        )
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )

