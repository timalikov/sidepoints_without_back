import re

import discord
from discord.ext import commands
from discord import app_commands

from bot_instance import get_bot
from translate import get_lang_prefix, translations

from database.dto.psql_services import Services_Database
from models.coupons import get_coupons
from services.utils import save_user_id
from services.messages.interaction import send_interaction_message
from views.dropdown.coupon_dropdown import CouponDropdownMenu
from views.find_view import FindView

bot = get_bot()

class FindCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="find", description="Find a user profile by their username.")
    @app_commands.describe(username="The username to find.")
    async def find(self, interaction: discord.Interaction, username: str):
        guild_id: int = interaction.guild_id if interaction.guild_id else None
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/find", 
            guild_id
        )
        await save_user_id(interaction.user.id)
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
            return
        pattern: str = r"<@(\d+)>"
        if re.fullmatch(pattern, username):
            user_id: int = int(username[2:-1])
            view = await FindView.create(user_id=user_id, guild_id=guild_id, lang=lang)
        else:
            view = await FindView.create(username=username, guild_id=guild_id, lang=lang)
        coupons: dict = await get_coupons(interaction.user)
        if coupons:
            coupon_dropdown = CouponDropdownMenu(coupons=coupons, lang=lang)
            view.add_item(coupon_dropdown)
        if view.no_user:
            await interaction.followup.send(
                content=translations["no_players"][lang],
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                embed=view.profile_embed,
                view=view,
                ephemeral=True
            )