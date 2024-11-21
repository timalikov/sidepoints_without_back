from typing import Literal, Dict

import discord

from bot_instance import get_bot
from translate import translations

from database.dto.psql_services import Services_Database
from views.buttons.base_button import BaseButton
from services.messages.interaction import send_interaction_message

bot = get_bot()


class ReplaceButton(BaseButton):
    def __init__(
        self,
        *,
        discord_server_id: int,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Replace Kicker",
            style=discord.ButtonStyle.green,
            custom_id="replace_button",
            row=row,
            emoji="🔄"
        )
        self.discord_server_id = discord_server_id
        self.lang = lang
        self._view_variables = ["disable_all_buttons", "customer", "kicker"]

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "replace", 
            interaction.guild.id if interaction.guild else None
        )
        await send_interaction_message(
            interaction=interaction,
            embed=discord.Embed(
                description=translations['replace_requested'][self.lang],
                colour=discord.Colour.gold()
            )
        )
        
        await self.view.disable_all_buttons()
        await self.replace_logic(interaction)

    async def replace_logic(self, interaction: discord.Interaction) -> None:
        from views.order_view import OrderView

        services_db = Services_Database()
        kicker_ids = await services_db.get_kickers()
        kicker: discord.User = self.view.kicker
        customer: discord.User = self.view.customer
        if kicker.id in kicker_ids:
            kicker_ids.remove(kicker.id)
        if customer.id in kicker_ids:
            kicker_ids.remove(customer.id)
        
        view = OrderView(
            customer=interaction.user,
            services_db=services_db,
            lang=self.lang,
            guild_id=self.discord_server_id
        )
        await view.message_manager.send_kickers_message()
