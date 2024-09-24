import asyncio
from typing import Callable, Any
import discord

import config
from bot_instance import get_bot

from models.private_channel import (
    create_private_discord_channel,
    send_connect_message_between_kicker_and_customer,
)
from services.messages.interaction import send_interaction_message
from services.refund_handler import RefundHandler
from services.refund_replace_message_manager import RefundReplaceManager
from services.timeout_refund_handler import TimeoutRefundHandler
from views.refund_replace import RefundReplaceView

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
        service_name: str,
        purchase_id: int,
        discord_server_id: int,
        sqs_client: Any
    ) -> None:
        super().__init__(timeout=None)
        self.kicker = kicker
        self.customer = customer
        self.kicker_username = kicker_username
        self.service_name = service_name
        self.purchase_id = purchase_id
        self.discord_server_id = discord_server_id

        self.already_pressed = False
        self.sqs_client = sqs_client
        self.user_interacted = False

        self.refund_handler = RefundHandler(sqs_client, purchase_id, customer, kicker)
        self.refund_manager = RefundReplaceManager(kicker=kicker, refund_handler=self.refund_handler, access_reject_view=self)

        self.timeout_refund_handler = TimeoutRefundHandler(
            timeout_seconds=60,
            on_timeout_callback=self.auto_reject  
        )

        asyncio.create_task(self.timeout_refund_handler.start())

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)

                await self.disable_access_reject_buttons()
                self.user_interacted = True


                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message="Button has already been pressed."
                )
            
        return decorator

    async def auto_reject(self):
        if not self.user_interacted:
            await self.refund_manager.start_periodic_refund_replace(self.customer, self.kicker, self.purchase_id)


    async def disable_access_reject_buttons(self):
        self.already_pressed = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(
        label="Accept",
        style=discord.ButtonStyle.green,
        custom_id="accept"
    )
    @check_already_pressed
    async def access(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        
        self.already_pressed = True
        self.timeout_refund_handler.cancel()
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)
        self.user_interacted = True


        await send_interaction_message(
            interaction=interaction,
            message=(
                f"Thanks for accepting the session with {self.customer.name}!"
            )
        )
        await self.refund_manager.stop_periodic_refund_replace()

        if not self.discord_server_id or str(self.discord_server_id) == str(config.MAIN_GUILD_ID):
            is_success, channel = await create_private_discord_channel(
                bot_instance=bot,
                guild_id=config.MAIN_GUILD_ID,
                challenged=self.kicker,
                challenger=self.customer,
                serviceName=self.service_name,
                kicker_username=self.kicker_username,
                purchase_id=self.purchase_id,
            )
        else:
            await send_connect_message_between_kicker_and_customer(
                challenged=self.kicker,
                challenger=self.customer,
                serviceName=self.service_name
            )
            channel = None

        return True, channel

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
        await interaction.response.defer()
        await send_interaction_message(
            interaction=interaction,
            message=(
                "You have rejected the session. The session is no longer valid."
            )
        )
        await self.refund_manager.stop_periodic_refund_replace()
        self.user_interacted = True

        view = RefundReplaceView(
            customer=self.customer,
            kicker=self.kicker,
            purchase_id=self.purchase_id,
            sqs_client=self.sqs_client
        )
        embed_message = discord.Embed(
            title=f"Sorry, the kicker {self.kicker.name} has not accepted the session.",
            colour=discord.Colour.blue(),
            description="Would you like a refund or replace the kicker?"
        )
        view.message = await self.customer.send(embed=embed_message, view=view)




        
