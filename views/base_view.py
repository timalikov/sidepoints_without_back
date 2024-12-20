import inspect
from typing import Any
from typing_extensions import Self

import discord
from discord.ui import View, Item

from services.view_collector import ViewCollector


class BaseView(View):
    async def disable_all_buttons(self):
        for item in self.children:
            if (
                isinstance(item, discord.ui.Button)
            ) or (
                isinstance(item, discord.ui.Select)
            ):
                item.disabled = True
        await self.message.edit(view=self)

    def __init__(
        self,
        *,
        timeout: float | None = 180,
        collector: ViewCollector = None
    ):
        super().__init__(timeout=timeout)
        self.collector = self._build_collector(collector)

    def _build_collector(self, collector: ViewCollector = None) -> ViewCollector:
        view_collector = collector or ViewCollector()
        stack: inspect.FrameInfo = inspect.stack()
        caller_instance: discord.ui.View = stack[1].frame.f_locals.get('self', None)
        view_collector.add_view(caller_instance)
        return view_collector
    
    def add_item(self, item: Item[Any]) -> Self:
        try:
            item.view = self
        except:
            raise
        finally:
            return super().add_item(item)
