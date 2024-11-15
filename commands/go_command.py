import discord
from discord.ext import commands
from discord import app_commands

from database.dto.psql_services import Services_Database
from database.dto.sql_order import Order_Database
from translate import get_lang_prefix, translations
from bot_instance import get_bot
from services.messages.interaction import send_interaction_message
from views.order_view import OrderView

from services.utils import save_user_id
from services.utils import get_guild_invite_link

bot = get_bot()


class GoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="go", description="Use this command to post your service request and summon ALL Kickers to take the order.")
    async def order_all(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id if interaction.guild_id else None
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
            return
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/order", 
            interaction.guild.id if interaction.guild else None
        )
        await save_user_id(interaction.user.id)
        order_data = {
            'user_id': interaction.user.id,
            'task_id': "ALL"
        }
        await Order_Database.set_user_data(order_data)
        main_link = await get_guild_invite_link(guild_id)
        services_db = Services_Database(app_choice="ALL")
        view = OrderView(
            customer=interaction.user,
            services_db=services_db,
            lang=lang,
            guild_id=guild_id
        )
        await interaction.followup.send(
            translations["order_dispatching"][lang].format(link=main_link),
            ephemeral=True
        )
        await view.send_all_messages()

