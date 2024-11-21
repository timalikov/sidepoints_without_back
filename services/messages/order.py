from typing import List
import asyncio
import discord

from config import (
    ORDER_CATEGORY_NAME,
    ORDER_CHANNEL_NAME,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME
)

from bot_instance import get_bot
from models.public_channel import get_or_create_channel_by_category_and_name
from message_constructors import _build_embed_message_order

bot = get_bot()


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
        self.embed_message = _build_embed_message_order(
            services_db=self.services_db,
            extra_text=extra_text,
            lang=view.lang,
            guild_id=self.guild_id,
            customer=customer
        )
        self.view = view
        
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
            sent_message = await channel.send(
                content="@everyone",
                embed=self.embed_message,
                view=self.view
            )
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
                sent_message = await kicker.send(
                    view=self.view,
                    embed=self.embed_message
                )
                self.messages.append(sent_message)
                await asyncio.sleep(1)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 5))
                    print(f"Rate limited. Retrying in {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    try:
                        sent_message = await kicker.send(
                            view=self.view,
                            embed=self.embed_message
                        )
                        self.messages.append(sent_message)
                    except discord.DiscordException as e:
                        print(f"Failed to send message to {kicker_id}: {e}")
                else:
                    print(f"Failed to send message to {kicker_id}: {e}")
                    continue
            except discord.DiscordException as e:
                print(f"General Discord error for user {kicker_id}: {e}")
                continue

    async def send_current_kickers_message(
        self,
        kickers: List[discord.User]
    ) -> None:

        for kicker in kickers:
            try:
                sent_message = await kicker.send(
                    embed=self.embed_message,
                    view=self.view
                )
                self.messages.append(sent_message)
            except discord.errors.Forbidden:
                print(f"Cannot send message to user: {kicker.id}")
            except discord.DiscordException:
                print(f"Failed to send message to user: {kicker.id}")