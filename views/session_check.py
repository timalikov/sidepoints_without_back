from typing import Any, Callable, Coroutine
from bot_instance import get_bot
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
        print("session_successful after 1 hour")
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
        await send_interaction_message(
            interaction=interaction,
            message="We are sorry to hear about that!\n Would you like a refund or customer support team will help you find an online kicker?"
        )

        view = RefundReplaceView(
            customer=self.customer,
            kicker=self.kicker,
            purchase_id=self.purchase_id,
            sqs_client=self.sqs_client
        )
        embed_message = discord.Embed(
            colour=discord.Colour.blue(),
            description="Would you like a refund or replace the kicker?"
        )

        await self.kicker.send(f"User <@{self.customer.id}> has stated that the session was not delivered. Your session is no longer valid. Customer Support officer will reach out to you shortly.")
        view.message = await self.customer.send(view=view, embed=embed_message)