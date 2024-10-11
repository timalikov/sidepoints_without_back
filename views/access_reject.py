from database.dto.psql_services import Services_Database
from typing import Callable, Any, Literal
import discord

import config
from bot_instance import get_bot

from models.private_channel import (
    create_private_discord_channel,
    send_connect_message_between_kicker_and_customer,
)
from services.messages.interaction import send_interaction_message
from services.refund_replace_message_manager import RefundReplaceManager
from views.refund_replace import RefundReplaceView
from translate import translations

bot = get_bot()

class AccessRejectView(discord.ui.View):
    """
    Send message with buttons Access and Reject.
    """

    def __init__(
        self,
        *,
        kicker: discord.User,
        customer: discord.User,
        kicker_username: str,
        service_name: str,
        purchase_id: int,
        discord_server_id: int,
        sqs_client: Any,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        super().__init__(timeout=None)
        self.kicker = kicker
        self.customer = customer
        self.kicker_username = kicker_username
        self.service_name = service_name
        self.purchase_id = purchase_id
        self.discord_server_id = discord_server_id

        self.already_pressed = False
        self.sqs_client = sqs_client
        self.user_interacted = False
        self.lang = lang

        self.refund_manager = RefundReplaceManager(
            access_reject_view=self,
            service_name=self.service_name,
            kicker=self.kicker,
            customer=self.customer,
            purchase_id=self.purchase_id,
            lang=self.lang
        )
        self.auto_reject()

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)
                await self.disable_access_reject_buttons()
                self.user_interacted = True
                return result
            await send_interaction_message(
                interaction=interaction,
                message=translations["button_already_pressed"][self.lang]
            )
            
        return decorator

    def auto_reject(self):
        if not self.user_interacted:
            self.refund_manager.start_periodic_refund_replace()

    async def disable_access_reject_buttons(self):
        self.already_pressed = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(
        label="Accept",
        style=discord.ButtonStyle.green,
        custom_id="accept"
    )
    @check_already_pressed
    async def access(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        await interaction.response.defer()
        await Services_Database().log_to_database(
            interaction.user.id, 
            "accept", 
            interaction.guild.id if interaction.guild else None
        )
        self.already_pressed = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)
        self.user_interacted = True
        await send_interaction_message(
            interaction=interaction,
            message=translations["accept_session_message"][self.lang].format(customer_name=self.customer.name)
        )
        await self.refund_manager.stop_periodic_refund_replace()
        guild: discord.Guild = bot.get_guild(self.discord_server_id)
        if guild.get_member(self.customer.id):
            is_success, channel = await create_private_discord_channel(
                bot_instance=bot,
                guild_id=self.discord_server_id,
                challenged=self.kicker,
                challenger=self.customer,
                serviceName=self.service_name,
                kicker_username=self.kicker_username,
                purchase_id=self.purchase_id,
                lang=self.lang
                )
        else:
            await send_connect_message_between_kicker_and_customer(
                challenger=self.customer,
                challenged=self.kicker,
                serviceName=self.service_name,
                lang=self.lang
            )

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
        await interaction.response.defer()
        await Services_Database().log_to_database(
            interaction.user.id, 
            "reject", 
            interaction.guild.id if interaction.guild else None
        )
        await send_interaction_message(
            interaction=interaction,
            message=translations["reject_session_message"][self.lang]
        )
        await self.refund_manager.stop_periodic_refund_replace()
        self.user_interacted = True

        view = RefundReplaceView(
            customer=self.customer,
            kicker=self.kicker,
            purchase_id=self.purchase_id,
            sqs_client=self.sqs_client,
            service_name=self.service_name,
            lang=self.lang,
            discord_server_id=self.discord_server_id
        )
        embed_message = discord.Embed(
            title=translations["kicker_not_accepted_title"][self.lang].format(kicker_name=self.kicker.name),
            colour=discord.Colour.blue(),
            description=translations["refund_replace_prompt"][self.lang]
        )
        view.message = await self.customer.send(embed=embed_message, view=view)
