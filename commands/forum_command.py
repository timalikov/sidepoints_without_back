import discord
from discord.ext import commands
from discord import app_commands

from translate import get_lang_prefix, translations
from bot_instance import get_bot
from services.utils import is_admin
from database.dto.psql_services import Services_Database
from services.messages.interaction import send_interaction_message
from models.thread_forum import start_posting
from models.forum import get_or_create_forum

bot = get_bot()


class ForumCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="forum", description="Create or update SideKick forum! [Only channel owner]")
    async def forum_command(self, interaction: discord.Interaction):
        guild_id: int = interaction.guild_id if interaction.guild_id else None
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/forum", 
            guild_id
        )
        guild: discord.guild.Guild = interaction.guild
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
            return
        try:
            forum_channel: discord.channel.ForumChannel = await get_or_create_forum(guild)
        except discord.DiscordException:
            await interaction.response.send_message(
                content=translations["not_community"][lang],
                ephemeral=True
            )
            return
        if not is_admin(interaction):
            await interaction.followup.send(
                content=translations["forum_no_permission"][lang],
                ephemeral=True
            )
            return
        await start_posting(forum_channel, guild, bot, order_type="ASC")
        await interaction.followup.send(
            content=translations["forum_posts_created"][lang],
            ephemeral=True
        )