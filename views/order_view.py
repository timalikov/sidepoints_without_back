import asyncio
from typing import Coroutine, List, Any, Literal
from datetime import datetime
import uuid
import discord

from config import (
    ORDER_CATEGORY_NAME,
    ORDER_CHANNEL_NAME,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME
)

from database.dto.psql_services import Services_Database
from services.utils import hide_half_string
from models.public_channel import get_or_create_channel_by_category_and_name
from views.buttons.order_go_button import OrderGoButton
from views.buttons.count_button import CountButton
from translate import translations

from bot_instance import get_bot

bot = get_bot()


class OrderView(discord.ui.View):
    """
    Like a Yandex taxi!

    Kickers will press the access button
    and customer get a message.
    """

    def __init__(
        self,
        *,
        customer: discord.User,
        guild_id: int,
        order_id: uuid.UUID = None,
        extra_text: str = "",
        lang: Literal["en", "ru"] = "en",
        services_db: Services_Database = None,
        go_command: bool = False
    ):
        super().__init__(timeout=15 * 60)
        self.customer: discord.User = customer
        self.pressed_kickers: List[discord.User] = []
        self.is_pressed = False
        self.services_db = services_db
        self.go_command = go_command
        self.messages = []  # for drop button after timeout
        self.created_at = datetime.now()
        self.guild_id = int(guild_id) if guild_id else None
        self.lang = lang
        self.webapp_order = False
        if order_id:
            self.order_id = order_id
            self.webapp_order = True
        else:
            self.order_id = str(uuid.uuid4())
        self.embed_message = self._build_embed_message_order(extra_text)
        self.boost_amount = None
        self.add_buttons()

    def add_buttons(self) -> None:
        self.add_item(OrderGoButton(lang=self.lang))
        self.add_item(CountButton(lang=self.lang))

    def _build_embed_message_order(self, extra_text: str) -> str:
        service_title = self.services_db.app_choice
        if not service_title:
            service_title = "All players"
        sex = self.services_db.sex_choice
        if not sex:
            sex = "Male/Female"
        language = self.services_db.language_choice
        if not language:
            language = "Русский" if self.lang == "ru" else "English"
        server = self.services_db.server_choice
        if not server:
            server = "Все" if self.lang == "ru" else "All"

        guild = bot.get_guild(self.guild_id)
        if self.customer:
            customer_discord_id: str = hide_half_string(str(self.customer.id))
        else:
            customer_discord_id: str = translations["order_from_webapp"][self.lang],
        embed = discord.Embed(
            title=translations["order_alert_title"][self.lang],
            description=translations["order_new_alert_new"][self.lang].format(
                customer_discord_id=customer_discord_id,
                choice=service_title,
                server_name=guild.name,
                language=language,
                gender=sex.capitalize(),
                game_server=server,
                extra_text=extra_text if extra_text else ""
            ),
            color=discord.Color.blue()
        )
        return embed
    
    async def send_current_kickers_message(
        self,
        kickers: List[discord.User]
    ) -> None:

        for kicker in kickers:
            try:
                sent_message = await kicker.send(embed=self.embed_message, view=self)
                self.messages.append(sent_message)
            except discord.errors.Forbidden:
                print(f"Cannot send message to user: {kicker.id}")
            except discord.DiscordException:
                print(f"Failed to send message to user: {kicker.id}")

    async def send_all_messages(self) -> None:
        await self.send_channel_message()
        await self.send_public_channel_message()
        await self.send_kickers_message()

    async def send_public_channel_message(self) -> None:
        """
        Without @everyone and buttons.
        """
        channel = await get_or_create_channel_by_category_and_name(
            category_name=GUIDE_CATEGORY_NAME,
            channel_name=GUIDE_CHANNEL_NAME,
            guild=bot.get_guild(self.guild_id)
        )
        try:
            await channel.send(embed=self.embed_message)
        except discord.errors.Forbidden:
            print(f"Cannot send message to channel: {channel.id}")
        except discord.DiscordException:
            print(f"Failed to send message to channel: {channel.id}")

    async def send_channel_message(self) -> None:
        channel = await get_or_create_channel_by_category_and_name(
            category_name=ORDER_CATEGORY_NAME,
            channel_name=ORDER_CHANNEL_NAME,
            guild=bot.get_guild(self.guild_id)
        )
        try:
            sent_message = await channel.send(content="@everyone", embed=self.embed_message, view=self)
            self.messages.append(sent_message)
        except discord.errors.Forbidden:
            print(f"Cannot send message to channel: {channel.id}")
        except discord.DiscordException:
            print(f"Failed to send message to channel: {channel.id}")

    async def send_kickers_message(self) -> None:
        kicker_ids = await self.services_db.get_kickers_by_service_title()
        for kicker_id in kicker_ids:
            try:
                kicker_id = int(kicker_id)
            except ValueError:
                print(f"ID: {kicker_id} is not int")
                continue
            try:
                kicker = await bot.fetch_user(kicker_id)
                await asyncio.sleep(0.5)  
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 5))
                    print(f"Rate limited while fetching user. Retrying in {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    try:
                        kicker = await bot.fetch_user(kicker_id)  
                    except discord.DiscordException as e:
                        print(f"Failed to fetch user {kicker_id} after retry: {e}")
                        continue
            if not kicker:
                continue
            try:
                sent_message = await kicker.send(view=self, embed=self.embed_message)
                self.messages.append(sent_message)
                await asyncio.sleep(1)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 5))
                    print(f"Rate limited. Retrying in {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    try:
                        sent_message = await kicker.send(view=self, embed=self.embed_message)
                        self.messages.append(sent_message)
                    except discord.DiscordException as e:
                        print(f"Failed to send message to {kicker_id}: {e}")
                else:
                    print(f"Failed to send message to {kicker_id}: {e}")
                    continue
            except discord.DiscordException as e:
                print(f"General Discord error for user {kicker_id}: {e}")
                continue

    async def on_timeout(self, stop_button_pressed: bool = False) -> Coroutine[Any, Any, None]:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        for message_instance in self.messages:
            await message_instance.edit(view=self)
        if stop_button_pressed:
            stopped_message_embed = discord.Embed(
                title=translations['order_terminated'][self.lang],
                description=translations['you_requested_stop_summon'][self.lang],
                color=discord.Color.red()
            )
            await self.customer.send(embed=stopped_message_embed, view=None)
            return
        if not self.is_pressed:
            timeout_message_embed = discord.Embed(
                title=translations['order_terminated'][self.lang],
                description=translations['timeout_message'][self.lang],
                color=discord.Color.red()
            )
            await self.customer.send(embed=timeout_message_embed, view=None)
