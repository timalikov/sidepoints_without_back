from typing import Any, Callable, Optional
import discord

from bot_instance import get_bot
from config import MAIN_GUILD_ID, TEST_ACCOUNTS

from views.order_view import OrderView
from database.dto.psql_services import Services_Database
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
        service_name: str,
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
        self.service_name = service_name
    
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
        await Services_Database().log_to_database(
            interaction.user.id, 
            "refund", 
            interaction.guild.id if interaction.guild else None
        )

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
        await Services_Database().log_to_database(
            interaction.user.id, 
            "replace", 
            interaction.guild.id if interaction.guild else None
        )
        await send_interaction_message(
            interaction=interaction,
            message=(
                "The replacement has been requested. "
                "We have also issued a refund for this service to you. "
                "Please wait while we look for a replacement kicker."
            )
        )
        
        await self.disable_all_buttons()
        await self.replace_logic(interaction)

    async def replace_logic(self, interaction: discord.Interaction) -> None:
        self.refund_handler.sqs_client.send_message(self.purchase_id)
        services_db = Services_Database()
        kicker_ids = await services_db.get_kickers()
        if self.kicker.id in kicker_ids:
            kicker_ids.remove(self.kicker.id)
        if self.customer.id in kicker_ids:
            kicker_ids.remove(self.customer.id)

        text_message_order_view = (
            f"New Order Alert: **{self.service_name}** [30 minutes]\n"
            f"You have a new order for a **{self.service_name}** in english"
        )
        view = OrderView(customer=interaction.user, services_db=services_db)
        for kicker_id in kicker_ids:
            try:
                kicker_id = int(kicker_id)
            except ValueError:
                print(f"ID: {kicker_id} is not int")
                continue
            kicker = bot.get_user(kicker_id)
            if not kicker:
                continue
            sent_message = await kicker.send(view=view, content=text_message_order_view)
            view.messages.append(sent_message)
