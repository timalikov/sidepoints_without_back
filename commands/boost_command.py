import re

import discord
from discord import app_commands
from discord.ext import commands

from bot_instance import get_bot
from views.boost_view import BoostView
from services.messages.interaction import send_interaction_message
from database.dto.psql_services import Services_Database
from translate import get_lang_prefix, translations
from services.utils import save_user_id

bot = get_bot()

class BoostCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="boost", description="Use this command to boost kickers!")
    @app_commands.describe(username="The username to find.")
    @app_commands.describe(amount='Amount USDT')
    async def boost(self, interaction: discord.Interaction, username: str, amount: float):
        if amount <= 0:
            await send_interaction_message(
                interaction=interaction,
                message="Amount less 1!"
            )
            return
        guild_id: int = interaction.guild_id if interaction.guild_id else None
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/boost", 
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
            view = BoostView(user_id=user_id, lang=lang, amount=amount)
        else:
            view = BoostView(user_name=username, lang=lang, amount=amount)
        await view.initialize()
        if view.no_user:
            if interaction.response.is_done():
                await interaction.followup.send(
                    content=translations["no_players"][lang],
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    content=translations["no_players"][lang],
                    ephemeral=True
                )
        else:
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=view.profile_embed,
                    view=view,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=view.profile_embed,
                    view=view,
                    ephemeral=True
                )
