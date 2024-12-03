from typing import Literal
import os

import discord

from config import TASK_DESCRIPTIONS, MAIN_GUILD_ID, FORUM_NAME
from bot_instance import get_bot
from translate import get_lang_prefix, translations

from message_constructors import create_profile_embed
from serializers.profile_serializer import serialize_profile_data
from services.logger.client import CustomLogger

logger = CustomLogger
bot = get_bot()

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


class GoButton(discord.ui.Button):
    def __init__(self, user_profile, lang: Literal["ru", "en"] = "en"):
        super().__init__(label="Go", style=discord.ButtonStyle.success, custom_id="play_user")
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        payment_link = f"https://sidekick.fans/payment/test"
        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    translations["payment_link"][self.lang].format(payment_link=payment_link), ephemeral=False
                )
            else:
                await interaction.response.send_message(
                    translations["payment_link"][self.lang].format(payment_link=payment_link), ephemeral=False
                )
        except discord.errors.NotFound:
            await logger.error_discord("Failed to send follow-up message. Interaction webhook not found.")

class StopButton(discord.ui.View):
    def __init__(self, stop_callback, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.stop_callback = stop_callback
        self.lang = lang

    @discord.ui.button(label="Stop notifications", style=discord.ButtonStyle.danger)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await self.stop_callback():
            message = translations["stopped_notifications"][self.lang]
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=False)
            else:
                await interaction.response.send_message(message, ephemeral=False)
        else:
            await logger.error_discord("Failed to stop all notifications")

class InformKickerButton(discord.ui.View):
    def __init__(self, kicker: discord.User, lang: Literal["ru", "en"] = "en"):
        super().__init__(timeout=None)
        self.kicker = kicker
        self.informed = False
        self.lang = lang

    @discord.ui.button(label="Inform Kicker", style=discord.ButtonStyle.primary, custom_id="inform_kicker_button")
    async def inform_kicker(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.informed:
            button.label = translations["kicker_informed"][self.lang]
            button.style = discord.ButtonStyle.success
            button.disabled = True
            self.informed = True

            await interaction.response.edit_message(view=self)


class StopDispatchingButton(discord.ui.Button):
    def __init__(self, *, order_view: discord.ui.View, order_dm_view: discord.ui.View):
        super().__init__(label="Stop Dispatching", style=discord.ButtonStyle.danger, custom_id="stop_dispatching")
        self.order_view = order_view
        self.order_dm_view = order_dm_view

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.edit_message(view=self.order_dm_view)
        await self.order_view.on_timeout(stop_button_pressed=True)