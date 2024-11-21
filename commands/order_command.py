import discord
from discord import app_commands
from discord.ext import commands

from models.payment import get_server_wallet_by_discord_id
from translate import get_lang_prefix, translations
from bot_instance import get_bot
from config import YELLOW_LOGO_COLOR

from database.dto.psql_services import Services_Database
from database.dto.sql_order import Order_Database
from core_command_choices import (
    servers_autocomplete,
    services_autocomplete,
    language_options,
    gender_options
)
from services.messages.interaction import send_interaction_message
from services.utils import save_user_id
from services.utils import get_guild_invite_link
from views.order_dm_view import OrderDMView
from views.order_view import OrderView
from web3_interaction.balance_checker import get_usdt_balance

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
        guild_id: int = interaction.guild_id if interaction.guild_id else None
        interaction_user_id: int = interaction.user.id
        interaction_user: discord.User = interaction.user
        lang = get_lang_prefix(guild_id)
        if not guild_id:
            await send_interaction_message(interaction=interaction, message=translations["not_dm"][lang])
            return
        await interaction.response.defer()
        await Services_Database().log_to_database(
            interaction_user_id, 
            "/order", 
            guild_id
        )
        await save_user_id(interaction_user_id)
        order_data = {
            'user_id': interaction_user_id,
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
            customer=interaction_user,
            services_db=services_db,
            lang=lang,
            guild_id=guild_id,
            extra_text=text
        )

        wallet: str = await get_server_wallet_by_discord_id(user_id=interaction_user_id)
        balance = get_usdt_balance(wallet) if wallet else 0
        # TODO: Replace in OrderMessageManager
        user_dm_view: OrderDMView = OrderDMView(order_view=view, balance=balance, lang=lang)
        await interaction_user.send(
            view=user_dm_view,
            embed=user_dm_view.embed_message
        )
        order_dispathing_embed = discord.Embed(
            title=translations["order_dispatching_title"][lang],
            description=translations["order_dispatching"][lang].format(link=main_link),
            color=discord.Color.from_rgb(*YELLOW_LOGO_COLOR)
        )
        if interaction.response.is_done():
            await interaction.followup.send(
                embed=order_dispathing_embed,
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                embed=order_dispathing_embed,
                ephemeral=False
            )
        await view.message_manager.send_all_messages()
