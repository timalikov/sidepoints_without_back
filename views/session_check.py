from typing import Any, Callable, Literal
from bot_instance import get_bot
from database.dto.psql_services import Services_Database
import discord
from services.messages.interaction import send_interaction_message
from services.sqs_client import SQSClient
from views.base_view import BaseView

from translate import translations, get_lang_prefix

bot = get_bot()

class SessionCheckView(BaseView):
    def __init__(
        self, 
        *, 
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,    
        channel: discord.VoiceChannel,
        lang: Literal["en", "ru"] = "en"
    ) -> None:
        super().__init__(timeout=60*60)
        self.customer = customer
        self.kicker = kicker
        self.purchase_id = purchase_id
        self.channel = channel
        self.already_pressed = False
        self.sqs_client = SQSClient()
        self.lang = get_lang_prefix(channel.guild.id)

    async def on_timeout(self):
        if not self.already_pressed:
            await self.session_successful()

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)

                self.already_pressed = True
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                
                await self.message.edit(view=self)

                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message=translations["button_already_pressed"][self.lang]
                )
            
        return decorator

    async def session_successful(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)

        await self.customer.send(translations["thank_you_customer"][self.lang].format(kicker=self.kicker.id))
        await self.kicker.send(translations["thank_you_kicker"][self.lang])

    @discord.ui.button(
        label="Yes",
        style=discord.ButtonStyle.green,
        custom_id="yes_button"
    )
    @check_already_pressed
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "session_check_yes", 
            interaction.guild.id if interaction.guild else None
        )

        self.already_pressed = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)

        await send_interaction_message(
            interaction=interaction,
            message=translations["thank_you_customer"][self.lang].format(kicker=self.kicker.id)
        )
        await self.kicker.send(translations["thank_you_kicker"][self.lang])

    @discord.ui.button(
        label="No",
        style=discord.ButtonStyle.red,
        custom_id="no_button"
    )
    @check_already_pressed
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "session_check_no", 
            interaction.guild.id if interaction.guild else None
        )
        await send_interaction_message(
            interaction=interaction,
            message=translations["support_ticket"][self.lang]
        )

        await self.kicker.send(translations["session_not_delivered"][self.lang].format(customer=self.customer.id))
