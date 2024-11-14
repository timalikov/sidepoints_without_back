from typing import Literal
import os

import discord

from config import TASK_DESCRIPTIONS, MAIN_GUILD_ID, FORUM_NAME
from bot_instance import get_bot
from translate import get_lang_prefix, translations

from message_constructors import create_profile_embed
from serializers.profile_serializer import serialize_profile_data
from database.dto.sql_forum_posted import ForumUserPostDatabase
from models.forum import find_forum

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
                print(f"HTTPException: {e}")
            except Exception as e:
                print(f"Unhandled exception: {e}")

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

class ShareButton(discord.ui.Button):
    def __init__(self, user_id, lang: Literal["ru", "en"] = "en"):
        super().__init__(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_profile")
        self.user_id = int(user_id)
        self.lang = lang

    async def callback(self, interaction: discord.Interaction):
        forum = await find_forum(guild=interaction.guild, forum_name=FORUM_NAME)
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(self.user_id, str(MAIN_GUILD_ID))
        if thread_id:
            thread = forum.get_thread(int(thread_id))
            profile_link = thread.jump_url
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(translations["profile_account_message"][self.lang].format(profile_link=profile_link), ephemeral=True)
                else:
                    await interaction.response.send_message(translations["profile_account_message"][self.lang].format(profile_link=profile_link), ephemeral=True)
            except discord.errors.NotFound:
                print("Failed to send follow-up message. Interaction webhook not found.")
        else:
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(translations["not_posted_yet"][self.lang], ephemeral=True)
                else:
                    await interaction.response.send_message(translations["not_posted_yet"][self.lang], ephemeral=True)
            except discord.errors.NotFound:
                print("Failed to send follow-up message. Interaction webhook not found.")

class ChatButton(discord.ui.Button):
    def __init__(self, user_id, lang: Literal["ru", "en"] = "en"):
        super().__init__(label="Chat", style=discord.ButtonStyle.secondary, custom_id="chat_user")
        try:
            self.user_id = int(user_id)
        except ValueError as e:
            self.user_id = 0
            print(f"Int ChatButton: {e}")
        self.lang = lang
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(self.user_id))
        if member:
            chat_link = translations["trial_chat_link"][self.lang].format(user_id=self.user_id)
        else:
            chat_link = translations["connect_chat_link"][self.lang].format(user_id=self.user_id)

        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"{chat_link}", ephemeral=False)
            else:
                await interaction.response.send_message(f"{chat_link}", ephemeral=False)
        except discord.errors.NotFound:
            print("Failed to send follow-up message. Interaction webhook not found.")

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
            print("Failed to send follow-up message. Interaction webhook not found.")

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
            print("Failed to stop all notifications")

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
    def __init__(self, *, order_view: discord.ui.View):
        super().__init__(label="Stop Dispatching", style=discord.ButtonStyle.danger, custom_id="stop_dispatching")
        self.order_view = order_view

    async def callback(self, interaction: discord.Interaction):
        await self.order_view.on_timeout()
        await interaction.response.send_message("Stopped dispatching orders", ephemeral=True)