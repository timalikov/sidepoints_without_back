import threading
import asyncio
from typing import List

from bot_instance import get_bot

bot = get_bot()


class BaseScheduleTask:
    tasks: List[threading.Thread]
    delay: int

    def __init__(self) -> None:
        self.tasks = []
        self.delay = 3600

    @staticmethod
    async def _main_function(delay: int, **kwargs) -> None:
        await asyncio.sleep(delay)
        raise NotImplementedError()

    def _start(self, **kwargs) -> None:
        asyncio.run_coroutine_threadsafe(
            self.__class__._main_function(**kwargs),
            loop=bot.loop
        )
    
    async def __call__(self, **kwargs) -> None:
        task = threading.Thread(
            target=self._start,
            kwargs=kwargs
        )
        self.tasks.append(task)
        task.start()
