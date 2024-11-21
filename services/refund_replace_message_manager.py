from typing import Any, Literal
import asyncio
import threading

import discord

from translate import translations
from bot_instance import get_bot
from config import MAIN_GUILD_ID

from services.sqs_client import SQSClient
from views.refund_replace import ReplaceView

bot = get_bot()

class RefundReplaceManager:
    def __init__(
        self,
        *,
        service_name: str,
        kicker: discord.User,
        customer: discord.User,
        purchase_id: int,
        discord_server_id: int = int(MAIN_GUILD_ID),
        lang: Literal["ru", "en"] = "en",
        access_reject_view: Any = None
    ) -> None:
        self.previous_message = None
        self.previous_view = None
        self.stop_event = asyncio.Event()
        self.user_interacted = False
        self.access_reject_view = access_reject_view
        self.service_name = service_name
        self.kicker = kicker
        self.customer = customer
        self.purchase_id = purchase_id
        self.lang = lang
        self.discord_server_id = discord_server_id

    async def send_refund_replace(self, start_timer: bool):
        if self.previous_message and self.previous_view:
            for item in self.previous_view.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
            try:
                await self.previous_message.edit(view=self.previous_view)
            except Exception as e:
                print(translations["failed_to_edit_message"][self.lang].format(error=e))

        timeout = 60 * 5 if start_timer else None

        view = ReplaceView(
            customer=self.customer,
            kicker=self.kicker,
            access_reject_view=self.access_reject_view,
            timeout=timeout,
            lang=self.lang,
            discord_server_id=self.discord_server_id,
            replace_manager=self
        )

        embed = discord.Embed(
            title=translations["kicker_not_accepted_title"][self.lang].format(kicker_name=self.kicker.name),
            description=translations["refund_replace_prompt"][self.lang],
            color=discord.Color.blue()
        )

        view.message = await self.customer.send(embed=embed, view=view) 
        self.previous_message = view.message
        self.previous_view = view

    def _start(self) -> None:
        asyncio.run_coroutine_threadsafe(
            self.periodic_refund_replace(),
            loop=bot.loop
        )

    async def periodic_refund_replace(self):
        for index in range(5):
            await asyncio.sleep(60)
            if self.stop_event.is_set():
                self.user_interacted = True
                return None
            start_timer = True if index == 4 else False
            await self.send_refund_replace(start_timer=start_timer)
            await self.kicker.send(
                embed=discord.Embed(
                    title="Are you there?",
                    description=translations["waiting_for_response"][self.lang].format(customer_id=self.customer.id),
                    colour=discord.Colour.red()
                )
            )

    def start_periodic_refund_replace(self):
        self.stop_event.clear()
        self.task = threading.Thread(
            target=self._start
        )
        self.task.start()
    
    async def stop_periodic_refund_replace(self):
        self.stop_event.set()
        
        if self.previous_view:
            for item in self.previous_view.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True
            try:
                await self.previous_message.edit(view=self.previous_view)
            except Exception as e:
                print(translations["failed_to_edit_message"][self.lang].format(error=e))
