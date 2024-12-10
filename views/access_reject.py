from typing import Literal
import discord

from bot_instance import get_bot
from translate import translations

from services.refund_replace_message_manager import RefundReplaceManager
from views.buttons.payment_button import PaymentButton
from views.buttons.reject_button import RejectButton
from views.base_view import BaseView

bot = get_bot()

class AccessRejectView(BaseView):
    """
    Send message with buttons Access and Reject.
    """

    def __init__(
        self,
        *,
        kicker: discord.User,
        customer: discord.User,
        service: dict,
        discord_server_id: int,
        purchase_id: int = None,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        super().__init__(timeout=60 * 5)
        self.kicker = kicker
        self.customer = customer
        self.discord_server_id = discord_server_id
        self.purchase_id = purchase_id
        self.service = service
        self.service_name = service["tag"]
        self.already_pressed = False
        self.lang = lang
        self.add_buttons()
        self.refund_manager = RefundReplaceManager(
            access_reject_view=self,
            service_name=self.service_name,
            kicker=self.kicker,
            customer=self.customer,
            purchase_id=self.purchase_id,
            lang=self.lang
        )
        self.auto_reject()

    def auto_reject(self):
        self.refund_manager.start_periodic_refund_replace()

    async def stop_refund_manager(self):
        await self.refund_manager.stop_periodic_refund_replace()

    async def disable_access_reject_buttons(self):
        self.already_pressed = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        if self in self.message._state._view_store._views:
            await self.message.edit(view=self)
        else:
            await self.message.edit(view=None)

    async def on_timeout(self) -> None:
        kicker_id = int(self.view.service["discord_id"])
        kicker_name = bot.get_user(kicker_id)
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if not self.already_pressed:
            await self.customer.send(
                embed=discord.Embed(
                    description=translations['kicker_reject_order'][self.lang].format(kicker_name=kicker_name)
                )
            )

    def add_buttons(self):
        payment_button = PaymentButton(
            discord_server_id=self.discord_server_id,
            customer=self.customer,
            lang=self.lang
        )
        payment_button.label = "Accept"
        reject_button = RejectButton(lang=self.lang)
        self.add_item(payment_button)
        self.add_item(reject_button)
