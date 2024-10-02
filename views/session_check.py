from typing import Any, Callable, Coroutine
from bot_instance import get_bot
from database.dto.psql_services import Services_Database
import discord
from services.messages.interaction import send_interaction_message
from services.sqs_client import SQSClient
from views.refund_replace import RefundReplaceView

bot = get_bot()

class SessionCheckView(discord.ui.View):
    def __init__(
        self, 
        *, 
        customer: discord.User,
        kicker: discord.User,
        purchase_id: int,    
        channel: Any
    ) -> None:
        super().__init__(timeout=60*60)
        self.customer = customer
        self.kicker = kicker
        self.purchase_id = purchase_id
        self.channel = channel
        self.already_pressed = False
        self.sqs_client = SQSClient()

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
                    message="Button has already been pressed."
                )
            
        return decorator

    async def session_successful(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)

        await self.customer.send(f"Thank you for using Sidekick!\n Hope you enjoyed the session with <@{self.kicker.id}>.")
        await self.kicker.send("Thank you for your service! The funds will be transferred to your wallet soon!")
        
        
    @discord.ui.button(
        label="Yes",
        style=discord.ButtonStyle.green,
        custom_id="yes_button"
    )
    @check_already_pressed
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        # await Services_Database().log_to_database(
        #     interaction.user.id, 
        #     "session_check_yes", 
        #     interaction.guild.id if interaction.guild else None
        # )

        self.already_pressed = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await self.message.edit(view=self)

        await send_interaction_message(
            interaction=interaction,
            message=f"Thank you for using Sidekick!\n Hope you enjoyed the session with <@{self.kicker.id}>."
        )
        await self.kicker.send("Thank you for your service! The funds will be transferred to your wallet soon!")

    @discord.ui.button(
        label="No",
        style=discord.ButtonStyle.red,
        custom_id="no_button"
    )
    @check_already_pressed
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer(ephemeral=True)
        # await Services_Database().log_to_database(
        #     interaction.user.id, 
        #     "session_check_no", 
        #     interaction.guild.id if interaction.guild else None
        # )
        await send_interaction_message(
            interaction=interaction,
            message="Please create a support ticket to get assistance from our customer support team in resolving the issue <#1233350206280437760>.\nRest assured, your funds are safe and securely locked in our wallet."
        )

        await self.kicker.send(f"User <@{self.customer.id}> has stated that the session was not delivered. Your session is no longer valid. Customer Support officer will reach out to you shortly.")