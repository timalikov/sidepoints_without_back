import discord
# from sql_challenge import SQLChallengeDatabase  # Adjusted import to use SQLChallengeDatabase
from sql_forum_posted import ForumUserPostDatabase
# from sql_profile import Profile_Database
from discord.ui import View
# from datetime import datetime
from config import MAIN_GUILD_ID, FORUM_ID, APP_CHOICES, LEADER_BOT_CHANNEL, CATEGORY_TO_TAG, FORUM_ID_LIST, LEADER_BOT_CHANNEL_LIST
from dotenv import load_dotenv
from message_constructors import create_profile_embed
import os
from bot_instance import get_bot
from getServices import DiscordServiceFetcher
bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES


class PlayView(View):
    def __init__(self, user_choice="ALL", username=None):
        super().__init__(timeout=None)
        self.userData = DiscordServiceFetcher(user_choice)
        self.no_user = False
        if username is not None:
            self.service = self.userData.find(username)
            if self.service != False:
                self.user_discord_id = self.service.get("")
                self.profile_embed = create_profile_embed(self.service)
            else:
                self.no_user = True
        else:
            self.service = self.userData.get_next()
            if  self.service != False:
                self.profile_embed = create_profile_embed(self.service)
            else:
                self.no_user = True

    @discord.ui.button(label="Go", style=discord.ButtonStyle.success, custom_id="play_user")
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        serviceId = self.service["serviceId"]
        discordServerId = interaction.guild.id
        # payment_link = f"https://sidekick.fans/payment/test"

        # payment_link = f"https://app.sidekick.fans/payment/{serviceId}?discordServerId={discordServerId}"
        payment_link = f"https://apptest.sidekick.fans/payment/{serviceId}?discordServerId={discordServerId}"
        await interaction.followup.send(f"To participate in this session, please complete your payment here: {payment_link}", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_user")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        self.service = self.userData.get_next()
        self.profile_embed = create_profile_embed(self.service)
        await interaction.edit_original_response(embed=self.profile_embed, view=self)

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_profile")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user_id = self.service["discordId"]
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, str(main_guild_id))

        if thread_id:
            thread = await bot.fetch_channel(int(thread_id))
            profile_link = thread.jump_url
            # profile_link = f"https://discord.com/channels/{main_guild_id}/{thread_id}"
            if interaction.response.is_done():
                await interaction.followup.send(f"Profile account: {profile_link}", ephemeral=True)
            else:
                await interaction.response.send_message(f"Profile account: {profile_link}", ephemeral=True)
        else:
            if interaction.response.is_done():
                await interaction.followup.send("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)
            else:
                await interaction.response.send_message("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)

    @discord.ui.button(label="Chat", style=discord.ButtonStyle.secondary, custom_id="chat_user")
    async def chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        user_id = self.service["discordId"]
        member = interaction.guild.get_member(int(user_id))
        if member:
            # username = member.name
            chat_link = f"Trial chat with the Kicker: <@!{int(user_id)}>.\n Click below to connect with user https://discord.com/users/{user_id}"
            if interaction.response.is_done():
                await interaction.followup.send(f"{chat_link}", ephemeral=True)
            else:
                await interaction.response.send_message(f"{chat_link}", ephemeral=True)
        else:
            chat_link = f"Click below to connect with user https://discord.com/users/{user_id}"
            if interaction.response.is_done():
                await interaction.followup.send(f"Chat with the user: {chat_link}", ephemeral=True)
            else:
                await interaction.followup.send(f"Chat with the user: {chat_link}", ephemeral=True)
