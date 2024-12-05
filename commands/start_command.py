import discord
from bot_instance import get_bot
from discord import app_commands
from discord.ext import commands

from database.dto.psql_services import Services_Database
from translate import get_lang_prefix, translations
from services.messages.interaction import send_interaction_message
from views.play_view import PlayView
from services.utils import save_user_id

bot = get_bot()


class StartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="start",
        description="Browse through the Kicker profiles and find your favourite to place an order."
    )
    async def play(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id if interaction.guild_id else None
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/go", 
            guild_id
        )
        await save_user_id(interaction.user.id)
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(
                interaction=interaction,
                message=translations["not_dm"][lang]
            )
            return
        view = await PlayView.create(user_choice="ALL", lang=lang, guild_id=guild_id)
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