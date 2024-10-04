from typing import Any, Callable, Optional, Literal
import discord

from bot_instance import get_bot
from config import MAIN_GUILD_ID
from translate import translations

from views.order_view import OrderView
from database.dto.psql_services import Services_Database
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
        lang: Literal["en", "ru"] = "en",
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
        self.refund_handler = RefundHandler(sqs_client, purchase_id, customer, kicker, lang=lang)
        self.service_name = service_name
        self.lang = lang
    
    async def on_timeout(self):
        if not self.already_pressed:
            await self.auto_refund()

    async def auto_refund(self) -> None:
        if not self.already_pressed:
            await self.disable_all_buttons()

            message = translations['timeout_auto_refund'][self.lang]
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
            message=translations['refund_requested'][self.lang]
        )

        await self.disable_all_buttons()

        await self.refund_handler.process_refund(
            interaction=None,
            success_message=translations['refund_success_customer'][self.lang],
            kicker_message=f"User <@{self.customer.id}> refunded the payment!",
            customer_message=translations['refund_success_customer'][self.lang],
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
            message=translations['replace_requested'][self.lang]
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

        text_message_order_view = translations['order_new_alert'][self.lang].format(choice=self.service_name)
        view = OrderView(customer=interaction.user, services_db=services_db, lang=MAIN_GUILD_ID)
        for kicker_id in kicker_ids:
            try:
                kicker_id = int(kicker_id)
            except ValueError:
                print(f"ID: {kicker_id} is not int")
                continue
            kicker = bot.get_user(kicker_id)
            if not kicker:
                continue
            try:
                sent_message = await kicker.send(view=view, content=text_message_order_view)
            except discord.DiscordException:
                continue
            view.messages.append(sent_message)
