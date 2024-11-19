from typing import Literal
from datetime import datetime
import discord

from database.dto.psql_services import Services_Database
from message_constructors import create_profile_embed
from services.messages.interaction import send_interaction_message
from services.sqs_client import SQSClient
from views.dropdown.boost_dropdown import BoostDropdownMenu
from views.dropdown.access_reject_dropdown import OrderAccessRejectDropdown
from views.buttons.base_button import BaseButton
from views.order_access_reject_view import OrderAccessRejectView
from translate import translations

from bot_instance import get_bot

bot = get_bot()

class OrderGoButton(BaseButton):
    def __init__(
        self,
        *,
        row: int | None = None,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(
            label="Go",
            style=discord.ButtonStyle.primary,
            custom_id="go",
            row=row,
            emoji="🎮"
        )
        self.lang = lang
        self._view_variables = [
            "services_db", "main_interaction", "created_at", "customer",
            "order_id", "pressed_kickers", "messages", "webapp_order", "guild_id"
            
        ]

    async def _bot_order(self, interaction: discord.Interaction, kicker: discord.User):
        services: list[dict] = await self.view.services_db.get_services_by_discordId(discordId=kicker.id)
        boost_services = await self.view.services_db.get_kicker_order_service(kicker.id)
        service = boost_services[0]
        embed = create_profile_embed(profile_data=service, lang=self.lang)
        embed.set_footer(text="The following Kicker has responded to your order. Click Go if you want to proceed.")
        order_dropdown = OrderAccessRejectDropdown(
            services=services,
            default_service=service,
            lang=self.lang
        )
        boost_dropdown = BoostDropdownMenu(
            target_service=service,
            need_send_boost=False,
            lang=self.lang
        )
        view = OrderAccessRejectView(
            customer=self.view.customer,
            main_interaction=interaction,
            service=service,
            kicker_id=kicker.id,
            order_view=self.view,
            guild_id=self.view.guild_id,
            lang=self.lang
        )
        view.add_item(order_dropdown)
        view.add_item(boost_dropdown)
        view.message = await self.view.customer.send(embed=embed, view=view)

        service_category = self.view.services_db.app_choice if self.view.services_db.app_choice == "ALL" else self.view.services_db.app_choice
        await self.view.services_db.save_order(
            timestamp=self.view.created_at,
            order_id=self.view.order_id,
            user_discord_id=self.view.customer.id,
            kicker_discord_id=kicker.id,
            order_category=service_category,
            respond_time=datetime.now(),
            service_price=service['service_price']
        )
        await send_interaction_message(interaction=interaction, message=translations['request_received'][self.lang])

    async def _webapp_order(self, interaction: discord.Interaction, kicker: discord.User):
        services = await self.view.services_db.get_services_by_discordId(kicker.id)
        sqs = SQSClient()
        sqs.send_order_confirm_message(order_id=self.view.order_id, service_id=services[0]["service_id"])
        await send_interaction_message(interaction=interaction, message=translations['request_received'][self.lang])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        kicker = interaction.user
        if kicker in self.view.pressed_kickers:
            return await send_interaction_message(interaction=interaction, message=translations['already_pressed'][self.lang])

        services: list[dict] = await self.view.services_db.get_services_by_discordId(discordId=kicker.id)
        kicker_score: int = await self.view.services_db.get_kicker_score(kicker.id)
        if not services or kicker_score < 100:
            return await send_interaction_message(interaction=interaction, message=translations['not_kicker'][self.lang])
        if not self.view.go_command:
            suitable_services = await self.view.services_db.get_kicker_order_service(kicker.id)
            if not suitable_services:
                return await send_interaction_message(interaction=interaction, message=translations['not_suitable_message'][self.lang])
        
        await Services_Database().log_to_database(
            interaction.user.id, 
            "kicker_go_after_order", 
            self.view.guild_id
        )
        self.view.pressed_kickers.append(kicker)

        if not self.view.webapp_order:
            await self._bot_order(interaction, kicker)
        else:
            await self._webapp_order(interaction, kicker)

        number_of_clicks = len(self.view.pressed_kickers)
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and item.label.isdigit():
                item.label = f"{number_of_clicks}"
        
        for message in self.view.messages:
            await message.edit(view=self.view)
        await interaction.message.edit(view=self.view)
