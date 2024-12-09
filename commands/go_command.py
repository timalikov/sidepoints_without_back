import discord
from discord.ext import commands
from discord import app_commands

from config import YELLOW_LOGO_COLOR

from database.dto.psql_services import Services_Database
from database.dto.sql_order import Order_Database
from translate import get_lang_prefix, translations
from bot_instance import get_bot
from services.messages.interaction import send_interaction_message
from views.order_view import OrderView
from views.order_dm_view import OrderDMView
from models.payment import (
    get_usdt_balance,
    get_server_wallet_by_discord_id,
)

from services.utils import save_user_id
from services.utils import get_guild_invite_link

bot = get_bot()


class GoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="go", description="Use this command to post your service request and summon ALL Kickers to take the order.")
    async def order_all(self, interaction: discord.Interaction):
        guild_id: int = interaction.guild_id if interaction.guild_id else None
        interaction_user: discord.User = interaction.user
        interaction_user_id: int = interaction_user.id
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
            return
        await interaction.response.defer()
        await Services_Database().log_to_database(
            interaction_user_id, 
            "/order", 
            interaction.guild.id if interaction.guild else None
        )
        await save_user_id(interaction_user_id)
        order_data = {
            'user_id': interaction_user_id,
            'task_id': "ALL"
        }
        await Order_Database.set_user_data(order_data)
        main_link = await get_guild_invite_link(guild_id)
        services_db = Services_Database(app_choice="ALL")
        wallet: str = await get_server_wallet_by_discord_id(user_id=interaction_user_id)
        balance = get_usdt_balance(wallet) if wallet else 0
        view = OrderView(
            customer=interaction_user,
            services_db=services_db,
            lang=lang,
            guild_id=guild_id,
            go_command=True
        )
        user_dm_view: OrderDMView = OrderDMView(
            order_view=view,
            balance=balance,
            lang=lang
        )
        await interaction_user.send(
            view=user_dm_view,
            embed=user_dm_view.embed_message
        )
        order_dispatching_embed = discord.Embed(
            title=translations["order_dispatching_title"][lang],
            description=translations["order_dispatching"][lang].format(link=main_link),
            color=discord.Color.from_rgb(*YELLOW_LOGO_COLOR)
        )
        await send_interaction_message(
            interaction=interaction,
            embed=order_dispatching_embed,
            ephemeral=False
        )
        await view.message_manager.send_all_messages()

