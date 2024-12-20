import re

import discord
from discord import app_commands
from discord.ext import commands

from bot_instance import get_bot
from translate import get_lang_prefix, translations

from models.coupons import connect_coupon_by_promo_code
from models.enums import CouponAddMessage
from services.messages.interaction import send_interaction_message

bot = get_bot()

class CouponCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="coupon", description="Use promo code!")
    @app_commands.describe(promo_code="Promo code.")
    async def use_promo_code(self, interaction: discord.Interaction, promo_code: str):
        await interaction.response.defer(ephemeral=True)
        lang = get_lang_prefix(interaction.guild_id)
        coupon_add_message = await connect_coupon_by_promo_code(interaction.user, promo_code)
        embeds: dict = {
            CouponAddMessage.SUCCESS: discord.Embed(
                description=translations["coupon_success_message"][lang],
                colour=discord.Colour.green()
            ),
            CouponAddMessage.HAS_OF_TYPE: discord.Embed(
                description=translations["coupon_already_exists_message"][lang],
                colour=discord.Colour.red()
            ),
            CouponAddMessage.INVALID_PROMO_CODE: discord.Embed(
                description=translations["invalid_coupon_message"][lang],
                colour=discord.Colour.red()
            ),
            CouponAddMessage.SERVER_PROBLEM: discord.Embed(
                description=translations["server_error_payment"][lang],
                colour=discord.Colour.red()
            )
        }
        await send_interaction_message(
            interaction=interaction,
            embed=embeds[coupon_add_message]
        )

