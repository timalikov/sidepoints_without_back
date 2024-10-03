import threading
import asyncio
from typing import Any, List, Literal

import discord

from views.session_check import SessionCheckView
from services.schedule_tasks.base import BaseScheduleTask
from bot_instance import get_bot

bot = get_bot()


class SessionDeliveryCheck(BaseScheduleTask):
    tasks: List[threading.Thread]
    delay: int

    def __init__(self) -> None:
        self.tasks = []
        self.delay = 3600

    @staticmethod
    async def _main_function(
        delay: int,
        *,
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        channel: Any,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        await asyncio.sleep(delay)
        message_embed = discord.Embed(
            colour=discord.Colour.dark_blue(),
            title=f"Hey @{customer.name}",
            description=(
                f"Has your session with kicker @{kicker.name} delivered?"
            )       
        )

        view = SessionCheckView(
            customer=customer,
            kicker=kicker,
            purchase_id=purchase_id,
            channel=channel
        )
        view.message = await customer.send(
            view=view,
            embed=message_embed
        )

    def _start(
        self,
        *,
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        channel: Any,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        asyncio.run_coroutine_threadsafe(
            self.__class__._main_function(
                delay=self.delay,
                customer=customer,
                kicker=kicker,
                purchase_id=purchase_id,
                channel=channel,
                lang=lang
            ),
            loop=bot.loop
        )
    
    async def __call__(
        self,
        *,
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        channel: Any,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        task = threading.Thread(
            target=self._start,
            kwargs={
                "customer": customer,
                "kicker": kicker,
                "purchase_id": purchase_id,
                "channel": channel,
                "lang": lang
            }
        )
        self.tasks.append(task)
        task.start()


session_delivery_check = SessionDeliveryCheck()
