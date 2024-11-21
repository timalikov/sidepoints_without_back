from typing import Any, Coroutine, Literal
import discord

from translate import translations
from config import (
    POINTS_IMAGE_URL,
    LINK_LEADERBOARD,
    YELLOW_LOGO_COLOR,
    INVITE_BOT_URL
)
from discord.ui import Button
from views.buttons.check_in_button import CheckInButton
from views.buttons.invite_user_button import InviteUserButton
from views.base_view import BaseView
from services.logger.client import CustomLogger
from bot_instance import get_bot

logger = CustomLogger
bot = get_bot()

class PointsView(BaseView):

    def __init__(
        self, 
        *,
        user: discord.User,
        username: str,
        total_points: int,
        rank: int,
        lang: Literal["en", "ru"] = "en",
    ):
        super().__init__(timeout=60 * 60)
        self.username = username
        self.user = user
        self.total_points = total_points
        self.rank = rank
        self.lang = lang
        self.message = None
        self.embed_message = self._build_embed_message_points()
        self.add_buttons()

    def add_buttons(self) -> None:
        # Временно убираем
        # self.add_item(
        #     discord.ui.Button(
        #         label="Add Sidekick to your server",
        #         url=INVITE_BOT_URL,
        #         style=discord.ButtonStyle.link,
        #         row=1
        #     )
        # )
        self.add_item(
            CheckInButton(user=self.user, total_points=self.total_points, lang=self.lang, row=3)
        )
        self.add_item(InviteUserButton(lang=self.lang))

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:
            await self.message.edit(embed=self.embed_message, view=self)

    def _build_embed_message_points(self):
        embed = discord.Embed(
            title=self.username + " " + translations["points"][self.lang],
            color=discord.Color.from_rgb(*YELLOW_LOGO_COLOR)
        )
        embed.add_field(
            name=translations["total_points"][self.lang],
            value=self.total_points,
            inline=True
        )
        embed.add_field(
            name=translations["leaderboard_ranking"][self.lang],
            value=self.rank if self.rank != 0 else "-",
            inline=True
        )
        embed.add_field(
            name=translations["check_out_details"][self.lang],
            value=f"{LINK_LEADERBOARD}?side_auth=DISCORD",
            inline=False
        )
        embed.set_image(url=POINTS_IMAGE_URL)
        return embed
