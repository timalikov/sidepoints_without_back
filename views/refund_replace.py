from typing import Any, Callable, Optional
from bot_instance import get_bot
from config import MAIN_GUILD_ID, TEST_ACCOUNTS
import discord
from models.private_channel_for_replace import create_channel_for_replace
from services.messages.customer_support_messenger import send_message_to_customer_support, send_message_to_super_kicker
from services.messages.interaction import send_interaction_message
from services.refund_handler import RefundHandler

bot = get_bot()

class RefundReplaceView(discord.ui.View):
    def __init__(
        self,
        *, 
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        sqs_client: Any,
        access_reject_view: Any = None,
        channel: Any = None,
        stop_task: Callable = None, 
        timeout: Optional[int] = 60 * 5

    ) -> None:
        super().__init__(timeout=timeout)
        self.customer = customer
        self.kicker = kicker
        self.purchase_id = purchase_id
        self.sqs_client = sqs_client
        self.access_reject_view = access_reject_view
        self.channel = channel
        self.stop_task = stop_task if stop_task is not None else lambda: None
        self.already_pressed = False
        self.refund_handler = RefundHandler(sqs_client, purchase_id, customer, kicker)
    
    async def on_timeout(self):
        if not self.already_pressed:
            await self.auto_refund()

    async def auto_refund(self) -> None:
        if not self.already_pressed:
            await self.disable_all_buttons()
            
            message=f"Sorry, we haven't received your decision in 5 minutes. The funds will be automatically refunded to your wallet."
            await self.customer.send(content=message)

            await self.refund_handler.process_refund(
                interaction=None,
                success_message="",
                kicker_message=f"User <@{self.customer.id}> refunded the payment!",
                customer_message=None,
                channel=self.channel
            )
    
    async def disable_all_buttons(self):
        if self.access_reject_view:
            await self.access_reject_view.disable_access_reject_buttons()

        if self.stop_task:
            self.stop_task()
        
        self.already_pressed = True

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await self.message.edit(view=self)

    @discord.ui.button(
        label="Refund",
        style=discord.ButtonStyle.red,
        custom_id="refund_button"
    )
    async def refund_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)

        await send_interaction_message(
            interaction=interaction,
            message="The refund has been requested."
        )

        await self.disable_all_buttons()

        await self.refund_handler.process_refund(
            interaction=None,
            success_message="Your funds will be refunded to your wallet soon! Until then, you can search for a new kicker.",
            kicker_message=f"User <@{self.customer.id}> refunded the payment!",
            customer_message=f"Your funds will be refunded to your wallet soon! Until then, you can search for a new kicker.",
            channel=self.channel
        )

    @discord.ui.button(
        label="Replace Kicker",
        style=discord.ButtonStyle.green,
        custom_id="replace_button"
    )
    async def replace_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await send_interaction_message(
            interaction=interaction,
            message=f"The replacement has been requested. Please wait ..."
        )
        
        await self.disable_all_buttons()
        await self.replace_logic(interaction)

    async def replace_logic(self, interaction: discord.Interaction) -> None:

        invite_url = await create_channel_for_replace(
            bot=bot,
            guild_id=MAIN_GUILD_ID,
            customer=self.customer
        )
        await send_interaction_message(
            interaction=interaction,
            message=f"Join the channel to replace the kicker: {invite_url}"
        )
        message=(
                "**Replacement has been purchased**\n"
                f"User: {self.customer.name}\n"
                f"Kicker: {self.kicker.name}\n"
                f"Voice room: {invite_url}"
            )

        if self.kicker.id not in TEST_ACCOUNTS and self.customer.id not in TEST_ACCOUNTS:
            await send_message_to_super_kicker(
                bot=bot,
                message=message
            )
            await send_message_to_customer_support(
                bot=bot,
                message=message
            )

        await self.kicker.send(f"User <@{self.customer.id}> has requested to replace you.")