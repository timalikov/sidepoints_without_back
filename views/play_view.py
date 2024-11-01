from typing import Literal

import discord
from discord.ui import View

import os
from dotenv import load_dotenv

from translate import translations
from config import APP_CHOICES, MAIN_GUILD_ID, FORUM_NAME
from services.kicker_sort_service import KickerSortingService
from services.messages.interaction import send_interaction_message
from message_constructors import create_profile_embed
from bot_instance import get_bot
from models.forum import find_forum
from models.payment import send_payment, get_usdt_balance_by_discord_user
from models.enums import PaymentStatusCodes
from views.top_up_view import TopUpView
from database.dto.psql_services import Services_Database
from database.dto.sql_forum_posted import ForumUserPostDatabase


bot = get_bot()
load_dotenv()

main_guild_id = int(os.getenv('MAIN_GUILD_ID'))

app_choices = APP_CHOICES

class PlayView(View):
    @classmethod
    async def create(cls, user_choice="ALL", username=None, lang: Literal["ru", "en"] = "en"):
        services_db = Services_Database(app_choice=user_choice)
        instance = cls(None, services_db, lang=lang)
        
        instance.services_db = services_db
        instance.kicker_sorting_service = KickerSortingService(services_db)

        if username:
            service = await services_db.get_services_by_username(username)
        else:
            service = await instance.kicker_sorting_service.fetch_first_service()

        if service:
            instance.set_service(service)
        else:
            instance.no_user = True

        return instance 
    
    def __init__(
        self,
        service: dict = None,
        services_db: Services_Database = None,
        lang: Literal["ru", "en"] = "en"
    ) -> None:
        super().__init__(timeout=None)
        self.service = service
        self.services_db = services_db
        self.no_user = False  
        self.profile_embed = None
        self.kicker_sorting_service = None
        self.lang = lang

    def set_service(self, service):
        """
        Helper function to set the service and create the embed.
        """
        self.service = service
        self.profile_embed = create_profile_embed(service, lang=self.lang)
        self.no_user = False  

    @discord.ui.button(label="Go", style=discord.ButtonStyle.success, custom_id="play_kicker")
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        discord_server_id = interaction.guild.id if interaction.guild else MAIN_GUILD_ID
        payment_status_code = await send_payment(
            user=interaction.user,
            target_service=self.service,
            discord_server_id=discord_server_id
        )
        balance = await get_usdt_balance_by_discord_user(interaction.user)
        try:
            guild: discord.Guild = bot.get_guild(
                int(discord_server_id)
            )
        except ValueError:
            guild: discord.Guild = None
        messages_kwargs = {
            PaymentStatusCodes.SUCCESS: {
                "embed": discord.Embed(
                    description=translations["success_payment"][self.lang].format(
                        amount=self.service["service_price"], balance=balance
                    ),
                    title="Success",
                    colour=discord.Colour.green()
                )
            },
            PaymentStatusCodes.NOT_ENOUGH_MONEY: {
                "embed": discord.Embed(
                    description=translations["not_enough_money_payment"][self.lang],
                    title="Not enough money",
                    colour=discord.Colour.gold()
                ),
                "view": TopUpView(
                    amount=float(self.service["service_price"]) - float(balance),
                    guild=guild,
                    lang=self.lang
                )
            },
            PaymentStatusCodes.SERVER_PROBLEM: {
                "embed": discord.Embed(
                    description=translations["server_error_payment"][self.lang],
                    colour=discord.Colour.red()
                )
            },
        }
        message_kwargs = messages_kwargs.get(payment_status_code, translations["server_error_payment"][self.lang])
        await send_interaction_message(
            interaction=interaction,
            **message_kwargs
        )
        button.disabled = True

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_kicker")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "next_kicker", 
            interaction.guild.id if interaction.guild else None
        )
        next_service = await self.kicker_sorting_service.get_next_valid_service()
        if next_service:
            self.set_service(next_service)
            await interaction.edit_original_response(embed=self.profile_embed, view=self)
        else:
            await interaction.followup.send(
                translations["no_valid_players"][self.lang],
                ephemeral=True
            )

    @discord.ui.button(label="Share", style=discord.ButtonStyle.secondary, custom_id="share_kicker")
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "share_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        user_id = self.service['discord_id']
        forum = await find_forum(guild=interaction.guild, forum_name=FORUM_NAME)
        thread_id = await ForumUserPostDatabase.get_thread_id_by_user_and_server(user_id, interaction.guild.id)

        message: str = ""
        if thread_id:
            try:
                thread = forum.get_thread(int(thread_id))
            except ValueError as e:
                print("Play View SHARE ERROR: {e}")
                thread = None
            if not thread:
                message = translations["profile_not_found"][self.lang]
            else:
                message = (
                    translations["share_profile_account"][self.lang]
                    .format(profile_link=thread.jump_url)
                )
        else:
            message = translations["sidekicker_account_not_posted"][self.lang]
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    @discord.ui.button(label="Chat", style=discord.ButtonStyle.secondary, custom_id="chat_kicker")
    async def chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "chat_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        user_id = self.service['discord_id']
        try:
            member = interaction.guild.get_member(int(user_id))
        except ValueError as e:
            print(f"CHAT ERROR: {e}")
            member = None
        if member:
            chat_link = translations["trial_chat_with_kicker"][self.lang].format(user_id=user_id)
            if interaction.response.is_done():
                await interaction.followup.send(chat_link, ephemeral=True)
            else:
                await interaction.response.send_message(chat_link, ephemeral=True)
        else:
            chat_link = translations["connect_with_user"][self.lang].format(user_id=user_id)
            await interaction.followup.send(
                translations["connect_with_user"][self.lang].format(user_id=user_id),
                ephemeral=True
            )

    @discord.ui.button(label="Boost", style=discord.ButtonStyle.success, custom_id="boost_kicker")
    async def boost(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await Services_Database().log_to_database(
            interaction.user.id, 
            "boost_kicker", 
            interaction.guild.id if interaction.guild else None
        )

        if self.service:
            payment_link = f"{os.getenv('WEB_APP_URL')}/boost/{self.service['profile_id']}?side_auth=DISCORD"
            await send_interaction_message(
                interaction=interaction,
                message=translations["boost_profile_link"][self.lang].format(boost_link=payment_link)
            )
        else:
            await send_interaction_message(
                interaction=interaction,
                message=translations["no_user_found_to_boost"][self.lang]
            )
            print(f"Boost button clicked, but no service found for user {interaction.user.id}")