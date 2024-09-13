import asyncio
from typing import Any
from discord.ext import tasks
import discord
from services.refund_handler import RefundHandler
from services.sqs_client import SQSClient
from views.refund_replace import RefundReplaceView

class RefundReplaceManager:
    def __init__(self, *, kicker: discord.User, refund_handler: Any, access_reject_view: Any = None) -> None:
        self.previous_message = None  
        self.previous_view = None
        self.kicker = kicker
        self.stop_event = asyncio.Event()
        self.user_interacted = False
        self.refund_handler = refund_handler
        self.access_reject_view = access_reject_view



    async def send_refund_replace(self, customer: discord.User, kicker: discord.User, purchase_id: int):
        if self.previous_message and self.previous_view:
            for item in self.previous_view.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
            try:
                await self.previous_message.edit(view=self.previous_view)
            except Exception as e:
                print(f"Failed to edit previous message: {e}")

        view = RefundReplaceView(
            customer=customer,
            kicker=kicker,
            purchase_id=purchase_id,
            sqs_client=SQSClient(),
            stop_task=self.stop_event.set,
            access_reject_view=self.access_reject_view
        )

        embed = discord.Embed(
            title="The kicker has not responded yet",
            description="Would you like to refund or replace the kicker?",
            color=discord.Color.blue()
        )

        self.previous_message = await customer.send(embed=embed, view=view) 
        self.previous_view = view

    @tasks.loop(seconds=60, count=5) 
    async def periodic_refund_replace(self, customer: discord.User, kicker: discord.User, purchase_id: int):
        if self.stop_event.is_set():  
            print("periodic_refund_replace task stopped.")
            self.user_interacted = True
            self.periodic_refund_replace.cancel() 
            return
        await self.send_refund_replace(customer, kicker, purchase_id)
        await self.kicker.send(f"User <@{customer.id}> is waiting for your response.\n Please Accept or Reject the session")

    async def start_periodic_refund_replace(self, customer: discord.User, kicker: discord.User, purchase_id: int):
        self.stop_event.clear()  
        await self.periodic_refund_replace.start(customer, kicker, purchase_id)

        if not self.user_interacted:
            await self.refund_handler.process_refund(
                interaction=None,
                success_message="",
                kicker_message=f"User <@{customer.id}> refunded the payment!",
                customer_message="Payment will be refunded to your wallet soon.",
                channel=None
            )
    
    async def stop_periodic_refund_replace(self):
        if self.periodic_refund_replace.is_running():
            self.stop_event.set()
            self.periodic_refund_replace.cancel()
            print("Manually stopped the periodic refund replace loop.")
            
            if self.previous_view:
                for item in self.previous_view.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                try:
                    await self.previous_message.edit(view=self.previous_view)
                except Exception as e:
                    print(f"Failed to edit previous message to disable buttons: {e}")
