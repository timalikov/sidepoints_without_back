import discord
from discord.ui import View


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
