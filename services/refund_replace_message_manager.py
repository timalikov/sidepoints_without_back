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

    async def send_refund_replace(self, customer: discord.User, kicker: discord.User, purchase_id: int, start_timer: bool):
        if self.previous_message and self.previous_view:
            for item in self.previous_view.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
            try:
                await self.previous_message.edit(view=self.previous_view)
            except Exception as e:
                print(f"Failed to edit previous message: {e}")

        timeout = 60 * 5 if start_timer else None

        view = RefundReplaceView(
            customer=customer,
            kicker=kicker,
            purchase_id=purchase_id,
            sqs_client=SQSClient(),
            stop_task=self.stop_event.set,
            access_reject_view=self.access_reject_view,
            timeout=timeout
        )

        embed = discord.Embed(
            title="The kicker has not responded yet",
            description="Would you like to refund or replace the kicker?",
            color=discord.Color.blue()
        )

        view.message = await customer.send(embed=embed, view=view) 
        self.previous_message = view.message
        self.previous_view = view

    @tasks.loop(seconds=60, count=5) 
    async def periodic_refund_replace(self, customer: discord.User, kicker: discord.User, purchase_id: int):
        if self.stop_event.is_set():  
            self.user_interacted = True
            self.periodic_refund_replace.cancel() 
            return
        
        if self.periodic_refund_replace.current_loop == 4:
            await self.send_refund_replace(customer, kicker, purchase_id, start_timer=True)
            await kicker.send(f"User <@{customer.id}> is waiting for your response.\nPlease Accept or Reject the session.")
        else:
            await self.send_refund_replace(customer, kicker, purchase_id, start_timer=False)
            await kicker.send(f"User <@{customer.id}> is waiting for your response.\nPlease Accept or Reject the session.")

    async def start_periodic_refund_replace(self, customer: discord.User, kicker: discord.User, purchase_id: int):
        self.stop_event.clear()  
        await self.periodic_refund_replace.start(customer, kicker, purchase_id)
    
    async def stop_periodic_refund_replace(self):
        if self.periodic_refund_replace.is_running():
            self.stop_event.set()
            self.periodic_refund_replace.cancel()
            
            if self.previous_view:
                for item in self.previous_view.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                try:
                    await self.previous_message.edit(view=self.previous_view)
                except Exception as e:
                    print(f"Failed to edit previous message to disable buttons: {e}")
