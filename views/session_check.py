from typing import Any, Callable
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
        channel: Any,
        session_delivery_check: Callable
        
    ) -> None:
        super().__init__(timeout=None)
        self.customer = customer
        self.kicker = kicker
        self.purchase_id = purchase_id
        self.channel = channel
        self.session_delivery_check = session_delivery_check
        self.already_pressed = False
        self.sqs_client = SQSClient()

    def check_already_pressed(func: Callable) -> Callable:
        async def decorator(self, interaction: discord.Interaction, *args, **kwargs) -> None:
            if not self.already_pressed:
                result: Any = await func(self, interaction, *args, **kwargs)

                self.already_pressed = True
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                
                await interaction.message.edit(view=self)

                return result
            else:
                await send_interaction_message(
                    interaction=interaction,
                    message="Button has already been pressed."
                )
            
        return decorator
        
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
        await interaction.message.edit(view=self)

        await send_interaction_message(
            interaction=interaction,
            message="Okay, enjoy your session!"
        )

        if self.session_delivery_check:
            await self.session_delivery_check.start(customer=self.customer, kicker=self.kicker, purchase_id=self.purchase_id, channel=self.channel)

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
            message="Okay, please select refund or replace kicker."
        )

        view = RefundReplaceView(
            customer=self.customer,
            kicker=self.kicker,
            purchase_id=self.purchase_id,
            sqs_client=self.sqs_client,
            channel=self.channel
        )
        embed_message = discord.Embed(
            colour=discord.Colour.blue(),
            description="Would you like a refund or replace the kicker?"
        )
        await self.customer.send(content=None, embed=embed_message, view=view)