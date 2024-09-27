from typing import Coroutine, List, Callable, Any
import uuid
import discord
import os

from database.dto.psql_services import Services_Database
from message_constructors import create_profile_embed
from config import MAIN_GUILD_ID
from services.messages.interaction import send_interaction_message
from models.guild import is_member_of_main_guild
from database.dto.sql_profile import log_to_database

from bot_instance import get_bot

bot = get_bot()


class OrderView(discord.ui.View):
    """
    Like a Yandex taxi!

    Kickers will pressing access button
    and customer get a message.
    """

    def __init__(self, *, customer: discord.User, services_db: Services_Database = None):
        super().__init__(timeout=15 * 60)
        self.customer: discord.User = customer
        self.pressed_kickers: List[discord.User] = []
        self.is_pressed = False
        self.services_db = services_db
        self.messages = []  # for drop button after timeout
        self.order_id = str(uuid.uuid4())

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        for message_instance in self.messages:
            try:
                await message_instance.delete()
            except Exception as e:
                print(e)
        if not self.is_pressed:
            await self.customer.send(
                content="Sorry, the dispatching countdown has ended and your order has not been completed successfully."
            )

    @discord.ui.button(label="Go", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        kicker = interaction.user
        if kicker in self.pressed_kickers:
            return await send_interaction_message(interaction=interaction, message="Already pressed")
        self.pressed_kickers.append(kicker)
        services: list[dict] = await self.services_db.get_services_by_discordId(discordId=kicker.id)
        if not services:
            return await send_interaction_message(interaction=interaction, message="You are not kicker!")
        service = services[0]
        embed = create_profile_embed(profile_data=service)
        embed.set_footer(text="The following Kicker has responded to your order. Click Go if you want to proceed.")
        view = OrderAccessRejectView(
            customer=self.customer, main_interaction=interaction, service_id=service['service_id'], order_view=self
        )
        view.message = await self.customer.send(embed=embed, view=view)
        await send_interaction_message(interaction=interaction, message="The customer has received your request!")

        service_category = self.services_db.app_choice if self.services_db.app_choice == "ALL" else await self.services_db.get_service_category_name(self.services_db.app_choice)
        await self.services_db.save_order(
            order_id=self.order_id,
            user_discord_id=self.customer.id,
            kicker_discord_id=kicker.id,
            order_category=service_category,
            respond_time=interaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            service_price=service['service_price']
        )

class OrderAccessRejectView(discord.ui.View):
    
    def __init__(
        self,
        *,
        customer: discord.User,
        main_interaction: discord.Interaction,
        service_id: int,
        order_view: Any,

    ) -> None:
        super().__init__(timeout=10 * 30)
        self.main_interaction = main_interaction
        self.service_id = service_id
        self.customer = customer
        self.already_pressed = False
        self.discord_service_id = MAIN_GUILD_ID
        self.order_view = order_view

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        await self.message.edit(view=None)

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)
                self.already_pressed = True
                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message="Button already pressed"
                )
        return decorator

    @discord.ui.button(
        label="Go",
        style=discord.ButtonStyle.green,
        custom_id="access"
    )
    @check_already_pressed
    async def access(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        self.order_view.is_pressed = True
        is_member = await is_member_of_main_guild(self.customer.id)
        if not is_member:
            await interaction.followup.send("Please join the server before proceeding: https://discord.gg/sidekick", ephemeral=True)
            return

        await log_to_database(interaction.user.id, "play_user")
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{self.service_id}?discordServerId={self.discord_service_id}&side_auth=DISCORD"
        await self.main_interaction.message.edit(content="Finished", embed=None, view=None)
        await interaction.followup.send(f"To participate in this session, please complete your payment here: {payment_link}", ephemeral=True)

    @discord.ui.button(
        label="Reject",
        style=discord.ButtonStyle.red,
        custom_id="reject"
    )
    @check_already_pressed
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await interaction.message.edit(embed=discord.Embed(description="Canceled"), view=None)
