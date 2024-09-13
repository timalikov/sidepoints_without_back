import asyncio
from typing import Callable

class TimeoutRefundHandler:
    def __init__(self, timeout_seconds: int, on_timeout_callback: Callable) -> None:

        self.timeout_seconds = timeout_seconds
        self.on_timeout_callback = on_timeout_callback
        self.task = None

    async def start(self) -> None:
        self.task = asyncio.create_task(self._run_countdown())

    async def _run_countdown(self) -> None:
        await asyncio.sleep(self.timeout_seconds)
        await self.on_timeout_callback()

    def cancel(self) -> None:
        if self.task:
            self.task.cancel()
            print("Refund Timer cancelled.")

