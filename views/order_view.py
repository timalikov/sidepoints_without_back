import asyncio
from typing import Coroutine, List, Callable, Any, Literal
from datetime import datetime
import uuid
import os
import discord

from config import (
    ORDER_CATEGORY_NAME,
    ORDER_CHANNEL_NAME,
)

from database.dto.psql_services import Services_Database
from message_constructors import create_profile_embed
from services.messages.interaction import send_interaction_message
from services.sqs_client import SQSClient
from models.public_channel import get_or_create_channel_by_category_and_name
from models.payment import get_usdt_balance_by_discord_user, send_payment
from models.enums import PaymentStatusCodes
from views.payment_button import PaymentButton
from views.top_up_view import TopUpView
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
        services_db: Services_Database = None
    ):
        super().__init__(timeout=15 * 60)
        self.customer: discord.User = customer
        self.pressed_kickers: List[discord.User] = []
        self.is_pressed = False
        self.services_db = services_db
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
        embed = discord.Embed(
            title=translations["order_alert_title"][self.lang],
            description=translations["order_new_alert_new"][self.lang].format(
                customer_discord_id=self.customer.id if self.customer else translations["order_from_webapp"][self.lang],
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
        await self.send_kickers_message()

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

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        for message_instance in self.messages:
            await message_instance.edit(view=self)
        if not self.is_pressed:
            await self.customer.send(content=translations['timeout_message'][self.lang])

    async def _bot_order(self, interaction: discord.Interaction, kicker: discord.User):
        services: list[dict] = await self.services_db.get_services_by_discordId(discordId=kicker.id)
        if not services:
            return await send_interaction_message(interaction=interaction, message=translations['not_kicker'][self.lang])
        service = services[0]
        embed = create_profile_embed(profile_data=service, lang=self.lang)
        embed.set_footer(text="The following Kicker has responded to your order. Click Go if you want to proceed.")
        view = OrderAccessRejectView(
            customer=self.customer,
            main_interaction=interaction,
            service=service,
            kicker_id=kicker.id,
            order_view=self,
            guild_id=self.guild_id,
            lang=self.lang
        )
        view.message = await self.customer.send(embed=embed, view=view)

        service_category = self.services_db.app_choice if self.services_db.app_choice == "ALL" else self.services_db.app_choice
        await self.services_db.save_order(
            timestamp=self.created_at,
            order_id=self.order_id,
            user_discord_id=self.customer.id,
            kicker_discord_id=kicker.id,
            order_category=service_category,
            respond_time=datetime.now(),
            service_price=service['service_price']
        )
        await send_interaction_message(interaction=interaction, message=translations['request_received'][self.lang])

    async def _webapp_order(self, interaction: discord.Interaction, kicker: discord.User):
        services = await self.services_db.get_services_by_discordId(kicker.id)
        sqs = SQSClient()
        sqs.send_order_confirm_message(order_id=self.order_id, service_id=services[0]["service_id"])
        await send_interaction_message(interaction=interaction, message=translations['request_received'][self.lang])

    @discord.ui.button(label="Go", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        kicker = interaction.user
        if kicker in self.pressed_kickers:
            return await send_interaction_message(interaction=interaction, message=translations['already_pressed'][self.lang])

        await Services_Database().log_to_database(
            interaction.user.id, 
            "kicker_go_after_order", 
            self.guild_id
        )
        self.pressed_kickers.append(kicker)

        if not self.webapp_order:
            await self._bot_order(interaction, kicker)
        else:
            await self._webapp_order(interaction, kicker)

        number_of_clicks = len(self.pressed_kickers)
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.label.isdigit():
                item.label = f"{number_of_clicks}"
        
        for message in self.messages:
            await message.edit(view=self)
        await interaction.message.edit(view=self)

    @discord.ui.button(label="0", style=discord.ButtonStyle.gray, disabled=True)
    async def count_clicks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)


class OrderAccessRejectView(discord.ui.View):
    
    def __init__(
        self,
        *,
        customer: discord.User,
        main_interaction: discord.Interaction,
        service: dict,
        kicker_id: int,
        guild_id: int,
        order_view: Any,
        lang: Literal["en", "ru"]

    ) -> None:
        super().__init__(timeout=10 * 30)
        self.main_interaction = main_interaction
        self.service = service
        self.service_id = service['service_id']
        self.kicker_id = kicker_id
        self.customer = customer
        self.already_pressed = False
        self.discord_service_id = guild_id
        self.order_view = order_view
        self.lang = lang

    async def on_timeout(self) -> Coroutine[Any, Any, None]:
        await self.message.edit(view=None)

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)
                self.already_pressed = True
                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message=translations['already_pressed'][self.lang]
                )
        return decorator

    @discord.ui.button(
        label="Go",
        style=discord.ButtonStyle.green,
        custom_id="access"
    )
    @check_already_pressed
    async def access(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        payment_status_code = await send_payment(
            user=interaction.user,
            target_service=self.service,
            discord_server_id=self.discord_service_id
        )
        balance = await get_usdt_balance_by_discord_user(interaction.user)
        messages_kwargs = {
            PaymentStatusCodes.SUCCESS: {
                "embed": discord.Embed(
                    description=translations["success_payment"][self.lang].format(
                        amount=self.service["service_price"], balance=balance
                    ),
                    title="Success",
                    colour=discord.Colour.green()
                )
            },
            PaymentStatusCodes.NOT_ENOUGH_MONEY: {
                "embed": discord.Embed(
                    description=translations["not_enough_money_payment"][self.lang],
                    title="Not enough money",
                    colour=discord.Colour.gold()
                ),
                "view": TopUpView(
                    amount=float(self.service["service_price"]) - float(balance),
                    lang=self.lang
                )
            },
            PaymentStatusCodes.SERVER_PROBLEM: {
                "embed": discord.Embed(
                    description=translations["server_error_payment"][self.lang],
                    colour=discord.Colour.red()
                )
            },
        }
        message_kwargs = messages_kwargs.get(payment_status_code, translations["server_error_payment"][self.lang])
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )
        button.disabled = True

    @discord.ui.button(
        label="Reject",
        style=discord.ButtonStyle.red,
        custom_id="reject"
    )
    @check_already_pressed
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await Services_Database().log_to_database(
            interaction.user.id, 
            "user_reject_after_order", 
            interaction.guild.id if interaction.guild else None
        )
        await interaction.message.edit(embed=discord.Embed(description=translations['canceled'][self.lang]), view=None)

    @discord.ui.button(label="Chat", style=discord.ButtonStyle.secondary, custom_id="chat_kicker")
    async def chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "chat_kicker", 
            interaction.guild.id if interaction.guild else None
        )
        chat_link = translations["trial_chat_with_kicker"][self.lang].format(user_id=self.kicker_id)
        await send_interaction_message(
            interaction=interaction,
            message=chat_link
        )

    @discord.ui.button(label="Boost", style=discord.ButtonStyle.success, custom_id="boost_kicker")
    async def boost(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "boost_kicker", 
            interaction.guild.id if interaction.guild else None
        )
        services: list[dict] = await self.order_view.services_db.get_services_by_discordId(discordId=self.kicker_id)
        if services:
            service = services[0]
            payment_link = f"{os.getenv('WEB_APP_URL')}/boost/{service['profile_id']}?side_auth=DISCORD"
            await send_interaction_message(
                interaction=interaction,
                message=translations["boost_profile_link"][self.lang].format(boost_link=payment_link)
            )
        else:
            await send_interaction_message(
                interaction=interaction,
                message=translations["no_user_found_to_boost"][self.lang]
            )
            print(f"Boost button clicked, but no service found for user {interaction.user.id}")
