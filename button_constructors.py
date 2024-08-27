from datetime import datetime
from bot_instance import get_bot
# from sql_profile import Profile_Database
from message_constructors import create_profile_embed
import discord
from sql_forum_posted import ForumUserPostDatabase
from config import TASK_DESCRIPTIONS, MAIN_GUILD_ID
bot = get_bot()


class AcceptView(discord.ui.View):
    def __init__(self, user_id, task_id, profile_data):
        super().__init__(timeout=None)
        self.profile_data = profile_data
        self.user_id = user_id
        self.task_id = task_id
        button = discord.ui.Button(label="Accept", style=discord.ButtonStyle.primary, custom_id=f"go_{user_id}")
        button.callback = self.button_callback  # Set the callback for the button
        self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        # Fetch profile data for the user_id
        profile_data = self.profile_data
        if profile_data:
            # user_id1 = interaction.user.id
            # user_id2 = profile_data['user_id']
            # price = profile_data['price']
            # wallet = profile_data.get("wallet", "not provided")  # Ensure wallet is fetched or default

            # # Create a challenge in the database
            # challenge_id = await SQLChallengeDatabase.create_challenge(
            #     user_id1,
            #     user_id2,
            #     datetime.now().strftime("%d-%m-%Y"),
            #     price,
            #     wallet,
            #     MAIN_GUILD_ID,
            #     self.task_id
            # )

            serviceId = self.profile_data['service_id']
            discordServerId = interaction.guild.id
            payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{serviceId}?discordServerId={discordServerId}"

            # Check if initial response is done, then follow up
            try:
                await interaction.response.send_message(
                    f"To participate in this session, please complete your payment here: {payment_link}",
                    ephemeral=True
                )
            except discord.errors.InteractionResponded:
                await interaction.followup.send(
                    f"To participate in this session, please complete your payment here: {payment_link}",
                    ephemeral=True
                )
            except discord.errors.HTTPException as e:
                print(f"HTTPException: {e}")
            except Exception as e:
                print(f"Unhandled exception: {e}")

class ButtonAcceptView(discord.ui.View):
    def __init__(self, user_id, task_id, order_id, profile_data):
        super().__init__(timeout=None)
        self.profile_data = profile_data
        self.user_id = int(user_id)  # Store user_id to use in the callback
        self.task_id = task_id
        self.order_id = order_id
        button = discord.ui.Button(label="Accept", style=discord.ButtonStyle.primary, custom_id=f"go_{user_id}")
        button.callback = self.button_callback  # Set the callback for the button
        self.add_item(button)  # Add the button to the view

    async def button_callback(self, interaction: discord.Interaction):
        kicker_data = self.profile_data
        kicker_data['task_desc'] = TASK_DESCRIPTIONS[self.task_id]
        # print("KICKER TASK DESK:", kicker_data['task_desc'])
        user = await bot.fetch_user(self.user_id)
        button = AcceptView(self.user_id, self.task_id)
        embed = create_profile_embed(kicker_data)
        await user.send(content=f"Here a new respond for your last order ✅\nPlease check it now!: {self.order_id}", embed=embed, view=button)

        # Send a confirmation message to the user who clicked the button
        await interaction.response.send_message(content="Your sidekick card has been sent to the user.", ephemeral=False)

class ShareButton(discord.ui.Button):
    def __init__(self, user_id):
        super().__init__(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_profile")
        self.user_id = int(user_id)

    async def callback(self, interaction: discord.Interaction):
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(self.user_id, str(MAIN_GUILD_ID))
        if thread_id:
            thread = await bot.fetch_channel(int(thread_id))
            profile_link = thread.jump_url
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(f"Profile account: {profile_link}", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Profile account: {profile_link}", ephemeral=True)
            except discord.errors.NotFound:
                print("Failed to send follow-up message. Interaction webhook not found.")
        else:
            try:
                if interaction.response.is_done():
                    await interaction.followup.send("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)
                else:
                    await interaction.response.send_message("The SideKicker account is not posted yet, please wait or you can share the username.", ephemeral=True)
            except discord.errors.NotFound:
                print("Failed to send follow-up message. Interaction webhook not found.")

class ChatButton(discord.ui.Button):
    def __init__(self, user_id):
        super().__init__(label="Chat", style=discord.ButtonStyle.secondary, custom_id="chat_user")
        self.user_id = int(user_id)
    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(self.user_id))
        if member:
            username = member.name
            chat_link = f"Trial chat with the Kicker: <@!{self.user_id}>.\n\n Also, click below to connect with user https://discord.com/users/{self.user_id}"
        else:
            chat_link = f"Click below to connect with user https://discord.com/users/{self.user_id}"

        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"{chat_link}", ephemeral=False)
            else:
                await interaction.response.send_message(f"{chat_link}", ephemeral=False)
        except discord.errors.NotFound:
            print("Failed to send follow-up message. Interaction webhook not found.")


class GoButton(discord.ui.Button):
    def __init__(self, user_profile):
        super().__init__(label="Go", style=discord.ButtonStyle.success, custom_id="play_user")

    async def callback(self, interaction: discord.Interaction):
        payment_link = f"https://sidekick.fans/payment/test"
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"{payment_link}", ephemeral=False)
            else:
                await interaction.response.send_message(f"{payment_link}", ephemeral=False)
        except discord.errors.NotFound:
            print("Failed to send follow-up message. Interaction webhook not found.")
