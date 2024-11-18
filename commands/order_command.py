import discord
from discord import app_commands
from discord.ext import commands

from translate import get_lang_prefix, translations
from services.messages.interaction import send_interaction_message
from database.dto.psql_services import Services_Database
from database.dto.sql_order import Order_Database
from bot_instance import get_bot
from translate import get_lang_prefix, translations
from core_command_choices import (
    servers_autocomplete,
    services_autocomplete,
    language_options,
    gender_options
)
from views.order_view import OrderView
from services.utils import save_user_id
from services.utils import get_guild_invite_link

bot = get_bot()


class OrderCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="order",
        description="Use this command to post your service request and summon Kickers to take the order."
    )
    @app_commands.autocomplete(choices=services_autocomplete)
    @app_commands.autocomplete(server=servers_autocomplete)
    @app_commands.choices(gender=gender_options)
    @app_commands.choices(language=language_options)
    @app_commands.describe(text='Order description')
    async def order(self,
        interaction: discord.Interaction,
        choices: str,
        server: str,
        gender: app_commands.Choice[str],
        language: app_commands.Choice[str],
        text: str = ""
        ):
            guild_id = interaction.guild_id if interaction.guild_id else None
            lang = get_lang_prefix(guild_id)
            if not guild_id:
                await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
                return
            await interaction.response.defer(ephemeral=True)
            await Services_Database().log_to_database(
                interaction.user.id, 
                "/order", 
                guild_id
            )
            await save_user_id(interaction.user.id)
            order_data = {
                'user_id': interaction.user.id,
                'task_id': choices
            }
            await Order_Database.set_user_data(order_data)
            main_link = await get_guild_invite_link(guild_id)
            services_db = Services_Database(
                app_choice=choices,
                sex_choice=gender.value,
                language_choice=language.value,
                server_choice=(
                    server 
                    if server.lower() != "all servers" 
                    and server.lower() != "no available servers"
                    else None
                )
            )
            view = OrderView(
                customer=interaction.user,
                services_db=services_db,
                lang=lang,
                guild_id=guild_id,
                extra_text=text
            )
            await interaction.followup.send(
                translations["order_dispatching"][lang].format(link=main_link),
                ephemeral=True
            )
            await view.send_all_messages()





