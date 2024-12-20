import os
from typing import Literal
import discord

from config import TASK_DESCRIPTIONS
from message_constructors import create_profile_embed
from serializers.profile_serializer import serialize_profile_data
from translate import get_lang_prefix, translations
from services.logger.client import CustomLogger

logger = CustomLogger


class AcceptView(discord.ui.View):
    def __init__(
        self,
        user_id,
        task_id,
        profile_data,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(timeout=None)
        self.profile_data = serialize_profile_data(profile_data)
        self.user_id = user_id
        self.task_id = task_id
        button = discord.ui.Button(label=translations["accept_button"][get_lang_prefix(user_id)], style=discord.ButtonStyle.primary, custom_id=f"go_{user_id}")
        button.callback = self.button_callback  # Set the callback for the button
        self.add_item(button)
        self.lang = lang

    async def button_callback(self, interaction: discord.Interaction):
        # Fetch profile data for the user_id
        profile_data = self.profile_data
        if profile_data:
            serviceId = self.profile_data['service_id']
            discordServerId = interaction.guild.id
            payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{serviceId}?discordServerId={discordServerId}&side_auth=DISCORD"

            # Check if initial response is done, then follow up
            try:
                await interaction.response.send_message(
                    translations["payment_message"][self.lang].format(payment_link=payment_link),
                    ephemeral=True
                )
            except discord.errors.InteractionResponded:
                await interaction.followup.send(
                    translations["payment_message"][self.lang].format(payment_link=payment_link),
                    ephemeral=True
                )
            except discord.errors.HTTPException as e:
                await logger.error_discord(f"HTTPException: {e}")
            except Exception as e:
                await logger.error_discord(f"Unhandled exception: {e}")


class ButtonAcceptView(discord.ui.View):
    def __init__(
        self,
        user_id,
        task_id,
        order_id,
        profile_data,
        lang: Literal["ru", "en"] = "en"
    ):
        super().__init__(timeout=None)
        self.profile_data = serialize_profile_data(profile_data)
        self.user_id = int(user_id)  # Store user_id to use in the callback
        self.task_id = task_id
        self.order_id = order_id
        button = discord.ui.Button(label=translations["accept_button"][get_lang_prefix(user_id)], style=discord.ButtonStyle.primary, custom_id=f"go_{user_id}")
        button.callback = self.button_callback
        self.add_item(button)
        self.lang = lang

    async def button_callback(self, interaction: discord.Interaction):
        kicker_data = self.profile_data
        kicker_data['task_desc'] = TASK_DESCRIPTIONS[self.task_id]
        user = await bot.fetch_user(self.user_id)
        button = AcceptView(self.user_id, self.task_id, lang=self.lang)
        embed = create_profile_embed(kicker_data)
        await user.send(content=f"Here a new respond for your last order ✅\nPlease check it now!: {self.order_id}", embed=embed, view=button)

        # Send a confirmation message to the user who clicked the button
        await interaction.response.send_message(content=translations["sidekick_card_message"][self.lang], ephemeral=False)
