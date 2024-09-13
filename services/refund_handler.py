import discord
from message_tasks import stop_all_messages
from services.messages.interaction import send_interaction_message

class RefundHandler:
    def __init__(self, sqs_client, purchase_id: int, customer: discord.User, kicker: discord.User) -> None:
        self.sqs_client = sqs_client
        self.purchase_id = purchase_id
        self.customer = customer
        self.kicker = kicker

    async def process_refund(self, *, interaction: discord.Interaction, success_message: str, kicker_message: str, customer_message: str, channel=None) -> None:
       
        if self.sqs_client.send_message(self.purchase_id):
            try:
                if interaction:
                    await send_interaction_message(interaction=interaction, message=success_message)
                
                if kicker_message:
                    await self.kicker.send(kicker_message)
                if customer_message:
                    await self.customer.send(customer_message)

                if channel:
                    await stop_all_messages(channel)

            except discord.HTTPException:
                print(f"Failed to send message to kicker {self.kicker.id}")
        else:
            await send_interaction_message(interaction=interaction, message="Failed to refund the payment. Please try again later.")
