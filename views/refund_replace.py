from typing import Any, Callable, Optional, Literal
import discord

from bot_instance import get_bot
from config import MAIN_GUILD_ID

from views.base_view import BaseView
from views.buttons.replace_button import ReplaceButton

bot = get_bot()

class ReplaceView(BaseView):
    def __init__(
        self,
        *, 
        customer: discord.User,
        kicker: discord.User,
        access_reject_view: Any = None,
        discord_server_id: int = int(MAIN_GUILD_ID),
        replace_manager = None,
        lang: Literal["en", "ru"] = "en",
        timeout: Optional[int] = 60 * 10
    ) -> None:
        super().__init__(timeout=timeout)
        self.customer = customer
        self.kicker = kicker
        self.access_reject_view = access_reject_view
        self.already_pressed = False
        self.lang = lang
        self.discord_server_id = discord_server_id
        self.replace_manager = replace_manager
        self.add_buttons()

    def add_buttons(self):
        replace_button = ReplaceButton(
            discord_server_id=self.discord_server_id,
        )
        self.add_item(replace_button)
    
    async def disable_all_buttons(self):
        if self.access_reject_view:
            await self.access_reject_view.disable_access_reject_buttons()
        
        self.already_pressed = True

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await self.message.edit(view=self)

        if self.replace_manager:
            await self.replace_manager.stop_periodic_refund_replace()
