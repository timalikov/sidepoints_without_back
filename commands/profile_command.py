import os

import discord
from discord import app_commands
from discord.ext import commands

from translate import get_lang_prefix, translations
from database.dto.psql_services import Services_Database
from bot_instance import get_bot
from services.messages.interaction import send_interaction_message
from views.exist_service import Profile_Exist
from services.utils import save_user_id

bot = get_bot()


class ProfileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Use this command if you wish to be part of the Sidekick Playmates network.")
    async def profile(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id if interaction.guild_id else None
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/profile", 
            interaction.guild.id if interaction.guild else None
        )
        await save_user_id(interaction.user.id)
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
            return
        profile_exist = Profile_Exist(discord_id=interaction.user.id, lang=lang)
        await profile_exist.initialize()
        if profile_exist.no_user:
            await send_interaction_message(interaction=interaction, message=translations["profile_not_created"][lang].format(link=os.getenv('WEB_APP_URL')))
        elif profile_exist.no_service:
            await send_interaction_message(interaction=interaction, message=translations["profile_no_service"][lang].format(link=os.getenv('WEB_APP_URL')))
        else:
            await interaction.followup.send(embed=profile_exist.profile_embed, view=profile_exist, ephemeral=True)

