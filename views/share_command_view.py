from database.dto.psql_services import Services_Database
import discord 
import os
from datetime import datetime, timedelta
from typing import Literal

from translate import translations
from config import MAIN_GUILD_ID

class ShareCommandView(discord.ui.View):
    cooldowns = {}  

    def __init__(
        self,
        bot,
        list_services,
        index,
        affiliate_channel_ids,
        lang: Literal["en", "ru"] = "en"
    ):
        super().__init__()
        self.bot = bot
        self.list_services = list_services
        self.index = index
        self.affiliate_channel_ids = affiliate_channel_ids
        self.user_id = self.list_services[self.index]["discord_id"]
        self.service_id = self.list_services[self.index]["service_id"]
        self.lang = lang

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
            title=(
                translations["share_embed_title"][self.lang]
                .format(username=username)
            ),
            description=(
                translations["share_embed_description"][self.lang]
                .format(service_description=service_description, category=category, price=price)
            )
        )
        if isinstance(service_image, list):
            service_image = service_image[0] if service_image else ""
        if service_image:
            embed.set_image(url=service_image) 

        for record in self.affiliate_channel_ids:
            channel_id = record["channel_id"]
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(embed=embed, view=self)
                except Exception as e:
                    print(f"Failed to send message to channel {channel_id}: {e}")

        message = translations["message_shared"][self.lang]
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
        
        message = translations["cooldown_message"][self.lang].format(hours=hours, minutes=minutes, seconds=seconds)
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    
    @discord.ui.button(label="Go", style=discord.ButtonStyle.success, custom_id="go_after_profile_share")
    async def go(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "/go_after_profile_share", 
            interaction.guild.id if interaction.guild else None
        )

        discord_server_id = interaction.guild.id
        
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{self.service_id}?discordServerId={discord_server_id}&side_auth=DISCORD"
        
        await interaction.followup.send(
            translations["payment_message"][self.lang].format(payment_link=payment_link),
            ephemeral=True
        )
