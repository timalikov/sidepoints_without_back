import discord
from discord.ext import commands

from bot_instance import get_bot
from discord import app_commands
from database.dto.sql_subscriber import Subscribers_Database
from database.dto.psql_services import Services_Database
from services.utils import save_user_id

bot = get_bot()


class SubscribeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="subscribe",
        description="Use this command to post your service request and summon Kickers to take the order."
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="Subscribe", value=1),
        app_commands.Choice(name="Unsubscribe", value=0),
    ])
    async def subscribe(self, interaction: discord.Interaction, choices: app_commands.Choice[int]):
        guild_id = interaction.guild_id if interaction.guild_id else None
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/subscribe", 
            guild_id
        )
        await save_user_id(interaction.user.id)
        if choices.value == 1:
            await Subscribers_Database.set_user_data(interaction.user.id)
            await interaction.followup.send(
                "You have successfully subscribed to the order command. Each time the /order command is used by users, you will receive a notification.",
                ephemeral=True
            )
        else:
            await Subscribers_Database.delete_user_data(interaction.user.id)
            await interaction.followup.send(
                "You have unsubscribed from the order command.",
                ephemeral=True
            )
