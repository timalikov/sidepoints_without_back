import asyncio
from typing import Callable, Any
import discord

import config
from bot_instance import get_bot

from models.private_channel import create_private_discord_channel
from services.messages.interaction import send_interaction_message
from services.refund_handler import RefundHandler
from services.timeout_refund_handler import TimeoutRefundHandler

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
        service_name: str,
        purchase_id: int,
        sqs_client: Any
    ) -> None:
        super().__init__(timeout=None)
        self.kicker = kicker
        self.customer = customer
        self.kicker_username = kicker_username
        self.channel_name = channel_name
        self.service_name = service_name
        self.purchase_id = purchase_id
        self.already_pressed = False
        self.sqs_client = sqs_client
        self.refund_handler = RefundHandler(sqs_client, purchase_id, customer, kicker)

        self.timeout_refund_handler = TimeoutRefundHandler(
            timeout_seconds=60,
            on_timeout_callback=self.auto_reject  
        )

        asyncio.create_task(self.timeout_refund_handler.start())

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)

                self.already_pressed = True
                self.timeout_refund_handler.cancel()

                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                
                await interaction.message.edit(view=self)

                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message="Button has already been pressed."
                )
            
        return decorator

    async def auto_reject(self):
        await self.refund_handler.process_refund(
            interaction=None,
            success_message="",
            kicker_message=(
                f"You haven't accepted/rejected the session within 15 minutes. The session with <@{self.customer.id}> is no longer valid, the funds have been refunded to the user."
            ),
            customer_message=(
                f"The kicker <@{self.kicker.id}> has not responded to the session within 15 minutes. The session is no longer valid and funds will be refunded to your wallet shortly. \n"
                "Please try again later or select another kicker."
            )
        )

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


        await send_interaction_message(
            interaction=interaction,
            message=(
                f"Thanks for accepting the session with {self.customer.name}!"
            )
        )

        is_success, channel = await create_private_discord_channel(
            bot_instance=bot,
            guild_id=config.MAIN_GUILD_ID,
            channel_name=self.channel_name,
            challenged=self.kicker,
            challenger=self.customer,
            serviceName=self.service_name,
            kicker_username=self.kicker_username,
            purchase_id=self.purchase_id,
        )

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
        await self.refund_handler.process_refund(
            interaction=interaction,
            success_message="The session is canceled",
            kicker_message=f"You rejected the session with <@{self.customer.id}>.",
            customer_message=f"Kicker <@{self.kicker.id}> rejected the session."
        )


        
