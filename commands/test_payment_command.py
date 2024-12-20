import discord
from discord import app_commands
from discord.ext import commands
from bot_instance import get_bot
from config import MAIN_GUILD_ID
from models.payment import send_payment
from database.dto.psql_services import Services_Database
from services.messages.interaction import send_interaction_message
from models.enums import PaymentStatusCode
from translate import translations,get_lang_prefix
from views.dropdown.top_up_dropdown import TopUpDropdownMenu
from views.buttons.payment_button import get_usdt_balance_by_discord_user
bot = get_bot()


class TestPaymentCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="test_payment", description="это тестовая команда для теста!")
    async def test_payment(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        dto = Services_Database()
        services: list = await dto.get_services_by_discordId(discordId=930005621728763904)
        service: dict = services[0]
        guild_id = interaction.guild_id if interaction.guild_id else None
        lang = get_lang_prefix(guild_id)
        balance = await get_usdt_balance_by_discord_user(interaction.user)
        payment_status_code = await send_payment(user=interaction.user, target_service=service, discord_server_id=MAIN_GUILD_ID)
        top_up_dropdown = TopUpDropdownMenu(lang=lang)
        top_up_dropdown_view = discord.ui.View(timeout=None)
        top_up_dropdown_view.add_item(top_up_dropdown)
        messages_kwargs = {
            PaymentStatusCode.SUCCESS: {
                "embed": discord.Embed(
                    description=translations["success_payment"][lang].format(
                        amount=service["service_price"], balance=balance
                    ),
                    title="✅ Payment Success",
                    colour=discord.Colour.green()
                )
            },
            PaymentStatusCode.NOT_ENOUGH_MONEY: {
                "embed": discord.Embed(
                    description=translations["not_enough_money_payment"][lang],
                    title="🔴 Not enough balance",
                    colour=discord.Colour.gold()
                ),
                "view": top_up_dropdown_view
            },
            PaymentStatusCode.SERVER_PROBLEM: {
                "embed": discord.Embed(
                    description=translations["server_error_payment"][lang],
                    colour=discord.Colour.red()
                )
            },
        }
        message_kwargs = messages_kwargs.get(payment_status_code, translations["server_error_payment"][lang])
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )


