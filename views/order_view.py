from typing import List
import discord

from database.dto.psql_services import Services_Database
from message_constructors import create_profile_embed
from views.access_reject import AccessRejectView
from models.private_channel import create_private_discord_channel
from services.messages.interaction import send_interaction_message
from background_tasks import session_delivery_check, session_start_check

from bot_instance import get_bot
import config

bot = get_bot()


class OrderView(discord.ui.View):
    """
    Like a Yandex taxi!

    Kickers will pressing access button
    and customer get a message.
    """

    def __init__(self, *, customer: discord.User, user_choises: str):
        super().__init__(timeout=600)
        self.customer: discord.User = customer
        self.user_choises = user_choises
        self.pressed_kickers: List[discord.User] = []

    @discord.ui.button(label="Access", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        kicker = interaction.user
        if kicker in self.pressed_kickers:
            return None
        services_db = Services_Database(app_choice=self.user_choises)
        services: list[dict] = services_db.get_services_by_discordId(discordId=kicker.id)
        if not services:
            return None
        service = services[0]
        embed = create_profile_embed(profile_data=service)
        view = AccessRejectView(kicker=customer)
        self.pressed_kickers.append(kicker)
        print(self.pressed_kickers)


class OrderAccessRejectView(AccessRejectView):

    async def access(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        is_success, channel = await create_private_discord_channel(
            bot_instance=bot,
            guild_id=config.MAIN_GUILD_ID,
            channel_name=self.channel_name,
            challenged=self.kicker,
            challenger=self.customer,
            serviceName=self.service_name,
            kicker_username=self.kicker_username
        )
        await send_interaction_message(interaction=interaction, message="Enjoy!")
        await session_start_check.start(customer=self.customer, kicker=self.kicker)
        await session_delivery_check.start(customer=self.customer, kicker=self.kicker)

    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await send_interaction_message(interaction=interaction, message="Order is cancel!")
        await self.customer.send(f"Kicker {self.kicker.name} caneled the order!")
        self.already_pressed = True
