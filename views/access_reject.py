from typing import Callable, Any
import discord

import config
from bot_instance import get_bot

from models.private_channel import create_private_discord_channel
from services.messages.interaction import send_interaction_message

bot = get_bot()


class AccessRejectView(discord.ui.View):
    """
    Send message with buttons Access and Reject.
    """

    def __init__(
        self,
        *,
        kicker: discord.User,
        customer: discord.User,
        kicker_username: str,
        channel_name: str,
        service_name: str
    ) -> None:
        super().__init__(timeout=None)
        self.kicker = kicker
        self.customer = customer
        self.kicker_username = kicker_username
        self.channel_name = channel_name
        self.service_name = service_name
        self.already_pressed = False

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
        label="Access",
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
        await send_interaction_message(interaction=interaction, message="Order is cancel!")
        await self.customer.send(f"Kicker {self.kicker.name} caneled the order!")
        self.already_pressed = True
