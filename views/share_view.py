import discord
from discord.ui import View
from config import MAIN_GUILD_ID  
from bot_instance import get_bot  
import os

bot = get_bot()

class ShareView(View):
    def __init__(self, user_id, service_id, discord_server_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.service_id = service_id
        self.discord_server_id = discord_server_id

    @discord.ui.button(label="Go", style=discord.ButtonStyle.success, custom_id="share_go_button")
    async def go(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{self.service_id}?discordServerId={self.discord_server_id}"
        
        is_member = await self.is_member_of_main_guild(interaction.user.id)
        if not is_member:
            await interaction.followup.send("Please join the server before proceeding: https://discord.gg/sidekick", ephemeral=True)
            return

        await interaction.followup.send(f"To participate in this session, please complete your payment here: {payment_link}", ephemeral=True)
        
    async def is_member_of_main_guild(self, user_id):
        main_guild = bot.get_guild(MAIN_GUILD_ID)
        if main_guild is None:
            return False
        member = main_guild.get_member(user_id)
        return member is not None
