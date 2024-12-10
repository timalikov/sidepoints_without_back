from typing import List
import asyncio
import discord

from config import (
    CHATTING_CHANNELS,
    ORDER_CATEGORY_NAME,
    ORDER_CHANNEL_NAME,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME,
    WEB3_CHATTING_CHANNEL_NAME
)

from bot_instance import get_bot
from services.logger.client import CustomLogger
from models.public_channel import get_or_create_channel_by_category_and_name
from message_constructors import _build_embed_message_order, _build_embed_message_order_2
from services.utils import get_gif_url_by_tag

bot = get_bot()
logger = CustomLogger


class OrderMessageManager:
    def __init__(
        self,
        customer: discord.User,
        guild_id: int,
        services_db: str,
        view: discord.ui.View,
        extra_text: str = "",
    ) -> None:
        self.guild_id = guild_id
        self.messages = []
        self.services_db = services_db
        self.public_channel_embed_message = _build_embed_message_order(
            services_db=self.services_db,
            extra_text=extra_text,
            lang=view.lang,
            guild_id=self.guild_id,
            customer=customer
        )
        gif_url: str = get_gif_url_by_tag(self.services_db.app_choice)
        self.channel_embed_message = _build_embed_message_order_2(
            services_db=self.services_db,
            extra_text=extra_text,
            lang=view.lang,
            guild_id=self.guild_id,
            customer=customer
        )
        if gif_url:
            self.public_channel_embed_message.set_image(url=gif_url)
            self.channel_embed_message.set_image(url=gif_url)
        self.view = view
        
    async def send_all_messages(self) -> None:
        await self.send_channel_message()
        await self.send_public_channel_message()
        await self.send_kickers_message()

    async def send_public_channel_message(self) -> None:
        """
        Without @everyone and buttons.
        """
        game_channel = await get_or_create_channel_by_category_and_name(
            category_name=ORDER_CATEGORY_NAME,
            channel_name=ORDER_CHANNEL_NAME,
            guild=bot.get_guild(self.guild_id)
        )
        chatting_channel = await get_or_create_channel_by_category_and_name(
            category_name=ORDER_CATEGORY_NAME,
            channel_name=WEB3_CHATTING_CHANNEL_NAME,
            guild=bot.get_guild(self.guild_id)
        )
        try:
            if self.services_db.app_choice == "ALL":
                sent_message = await game_channel.send(
                    content="@everyone",
                    embed=self.channel_embed_message,
                    view=self.view
                )
                sent_message2 = await chatting_channel.send(
                    content="@everyone",
                    embed=self.channel_embed_message,
                    view=self.view
                )
                self.messages.append(sent_message, sent_message2)
            elif self.services_db.app_choice.lower() in CHATTING_CHANNELS:
                sent_message = await chatting_channel.send(
                    content="@everyone",
                    embed=self.channel_embed_message,
                    view=self.view
                )
                self.messages.append(sent_message)
            else:
                sent_message = await game_channel.send(
                    content="@everyone",
                    embed=self.channel_embed_message,
                    view=self.view
                )
                self.messages.append(sent_message)
        except discord.errors.Forbidden:
            await logger.error_discord(f"Cannot send message to channel: {game_channel.id}")
        except discord.DiscordException:
            await logger.error_discord(f"Failed to send message to channel: {game_channel.id}")

    async def send_channel_message(self) -> None:
        channel = await get_or_create_channel_by_category_and_name(
            category_name=GUIDE_CATEGORY_NAME,
            channel_name=GUIDE_CHANNEL_NAME,
            guild=bot.get_guild(self.guild_id)
        )
        try:
            await channel.send(
                embed=self.public_channel_embed_message,
            )
        except discord.errors.Forbidden:
            await logger.error_discord(f"Cannot send message to channel: {channel.id}")
        except discord.DiscordException:
            await logger.error_discord(f"Failed to send message to channel: {channel.id}")

    async def send_kickers_message(self) -> None:
        kicker_ids = await self.services_db.get_kickers_by_service_title()
        for kicker_id in kicker_ids:
            try:
                kicker_id = int(kicker_id)
            except ValueError:
                await logger.error_discord(f"ID: {kicker_id} is not int")
                continue
            try:
                kicker = await bot.fetch_user(kicker_id)
                await asyncio.sleep(0.5)  
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 5))
                    await logger.error_discord(f"Rate limited while fetching user. Retrying in {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    try:
                        kicker = await bot.fetch_user(kicker_id)  
                    except discord.DiscordException as e:
                        await logger.error_discord(f"Failed to fetch user {kicker_id} after retry: {e}")
                        continue
            if not kicker:
                continue
            try:
                sent_message = await kicker.send(
                    view=self.view,
                    embed=self.channel_embed_message
                )
                self.messages.append(sent_message)
                await asyncio.sleep(1)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 5))
                    await logger.error_discord(f"Rate limited. Retrying in {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    try:
                        sent_message = await kicker.send(
                            view=self.view,
                            embed=self.channel_embed_message
                        )
                        self.messages.append(sent_message)
                    except discord.DiscordException as e:
                        await logger.error_discord(f"Failed to send message to {kicker_id}: {e}")
                else:
                    await logger.error_discord(f"Failed to send message to {kicker_id}: {e}")
                    continue
            except discord.DiscordException as e:
                await logger.error_discord(f"General Discord error for user {kicker_id}: {e}")
                continue

    async def send_current_kickers_message(
        self,
        kickers: List[discord.User]
    ) -> None:

        for kicker in kickers:
            try:
                sent_message = await kicker.send(
                    embed=self.channel_embed_message,
                    view=self.view
                )
                self.messages.append(sent_message)
            except discord.errors.Forbidden:
                await logger.error_discord(f"Cannot send message to user: {kicker.id}")
            except discord.DiscordException:
                await logger.error_discord(f"Failed to send message to user: {kicker.id}")
