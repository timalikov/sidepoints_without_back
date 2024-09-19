import threading
import asyncio
from typing import Any, List

import discord

from views.session_check import SessionCheckView
from bot_instance import get_bot

bot = get_bot()


class SessionDeliveryCheck:
    tasks: List[threading.Thread]
    delay: int

    def __init__(self) -> None:
        self.tasks = []
        self.delay = 3600

    async def _main_function(
        self,
        *,
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        channel: Any,
    ) -> None:
        await asyncio.sleep(self.delay)
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
    ) -> None:
        loop = bot.loop
        loop.run_until_complete(
            self._main_function(
                customer=customer,
                kicker=kicker,
                purchase_id=purchase_id,
                channel=channel,
            )
        )
    
    async def __call__(
        self,
        *,
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,
        channel: Any,
    ) -> None:
        task = threading.Thread(
            target=self._start,
            kwargs={
                "customer": customer,
                "kicker": kicker,
                "purchase_id": purchase_id,
                "channel": channel,
            }
        )
        self.tasks.append(task)
        task.start()


session_delivery_check = SessionDeliveryCheck()
