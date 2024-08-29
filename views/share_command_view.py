from config import MAIN_GUILD_ID
from datetime import datetime, timedelta
import discord 
import os

class ShareCommandView(discord.ui.View):
    cooldowns = {}  

    def __init__(self, bot, list_services, index, affiliate_channel_ids):
        super().__init__()
        self.bot = bot
        self.list_services = list_services
        self.index = index
        self.affiliate_channel_ids = affiliate_channel_ids
        self.user_id = self.list_services[self.index]["discord_id"]
        self.service_id = self.list_services[self.index]["service_id"]


    async def share(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = datetime.utcnow()

        if self.is_on_cooldown(user_id, now):
            return await self.send_cooldown_message(interaction, user_id, now)
        
        self.cooldowns[user_id] = now

        username = self.list_services[self.index]["profile_username"]
        service_description = self.list_services[self.index]["service_description"]
        category = self.list_services[self.index]["service_type_name"]
        price = self.list_services[self.index]["service_price"]
        service_image = self.list_services[self.index].get("service_image", None)  

        embed = discord.Embed(
            title=f"Username: {username}",
            description=f"**Description:** {service_description}\n**Category:** {category}\n**Price:** ${price}"
        )
        if service_image:
            embed.set_image(url=service_image) 

        channel_ids = ['1276403616961400916']
        # for record in self.affiliate_channel_ids:
        for record in channel_ids:
            # channel_id = record["channel_id"]
            channel_id = record
            channel = await self.bot.fetch_channel(channel_id)
            if channel:
                try:
                    await channel.send(embed=embed, view=self)
                except Exception as e:
                    print(f"Failed to send message to channel {channel_id}: {e}")

        message = "Message has been shared across all affiliate channels."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    
    def is_on_cooldown(self, user_id, now):
        if user_id in self.cooldowns:
            last_shared_time = self.cooldowns[user_id]
            cooldown_time = timedelta(hours=6)
            if now < last_shared_time + cooldown_time:
                return True
        return False

    async def send_cooldown_message(self, interaction, user_id, now):
        last_shared_time = self.cooldowns[user_id]
        remaining_time = last_shared_time + timedelta(hours=6) - now
        hours, minutes = divmod(int(remaining_time.seconds), 3600)
        minutes, seconds = divmod(minutes, 60)
        
        message = f"Please wait {hours} hours {minutes} minutes {seconds} seconds before sharing again."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    
    @discord.ui.button(label="Go", style=discord.ButtonStyle.success, custom_id="share_go_button")
    async def go(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        discord_server_id = interaction.guild.id
        
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{self.service_id}?discordServerId={discord_server_id}"
        
        is_member = await self.is_member_of_main_guild(interaction.user.id)
        if not is_member:
            await interaction.followup.send("Please join the server before proceeding: https://discord.gg/sidekick", ephemeral=True)
            return

        await interaction.followup.send(f"To participate in this session, please complete your payment here: {payment_link}", ephemeral=True)
        
    async def is_member_of_main_guild(self, user_id):
        main_guild = self.bot.get_guild(MAIN_GUILD_ID)
        if main_guild is None:
            return False
        member = main_guild.get_member(user_id)
        return member is not None
