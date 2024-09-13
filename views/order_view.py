from typing import Coroutine, List, Callable, Any
import discord
import os

from database.dto.psql_services import Services_Database, APP_CHOICES
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

    def __init__(self, *, customer: discord.User, user_choises: str = "ALL", is_direct_message: bool = False):
        super().__init__(timeout=15*60)
        self.customer: discord.User = customer
        self.services_db = Services_Database(app_choice=user_choises)
        self.pressed_kickers: List[discord.User] = []
        self.is_direct_message = is_direct_message
        self.is_pressed = False
        self.user_choises = user_choises

    async def send_all_kickers_with_current_category(self, text: str) -> None:
        for _ in range(100):
            service = await self.services_db.get_next_service()
            if not service:
                return None
            kicker_id: int = service.get("discord_id", "")
            try:
                kicker_id = int(kicker_id)
            except ValueError:
                print(f"ID: {kicker_id} is not int")
                return None
            kicker = bot.get_user(kicker_id)
            if not kicker:
                continue
            view = self.__class__(customer=self.customer, is_direct_message=True)
            view.message = await kicker.send(content=text, view=view)

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        if not self.is_direct_message and not self.is_pressed:
            choices = (
                "All players"
                if self.user_choises == "ALL"
                else await self.services_db.get_service_category_name(
                    service_type_id=self.user_choises
                )
            )
            await self.send_all_kickers_with_current_category(
                f"New Order Alert: **{choices}** [30 minutes]\n"
                f"You have a new order for a **{choices}** in english"
            )
        if self.is_direct_message and not self.is_pressed:
            await self.customer.send(content="Sorry! No one took your order!")
        await self.message.edit(view=None)

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
        view = OrderAccessRejectView(
            customer=self.customer, main_interaction=interaction, service_id=service['service_id']
        )
        view.message = await self.customer.send(embed=embed, view=view)
        self.is_pressed = True
        await send_interaction_message(interaction=interaction, message="The customer has received your request!")


class OrderAccessRejectView(discord.ui.View):
    
    def __init__(
        self,
        *,
        customer: discord.User,
        main_interaction: discord.Interaction,
        service_id: int,
    ) -> None:
        super().__init__(timeout=500)
        self.main_interaction = main_interaction
        self.service_id = service_id
        self.customer = customer
        self.already_pressed = False
        self.discord_service_id = MAIN_GUILD_ID

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
        is_member = await is_member_of_main_guild(self.customer.id)
        if not is_member:
            await interaction.followup.send("Please join the server before proceeding: https://discord.gg/sidekick", ephemeral=True)
            return

        await log_to_database(interaction.user.id, "play_user")
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{self.service_id}?discordServerId={self.discord_service_id}"
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
