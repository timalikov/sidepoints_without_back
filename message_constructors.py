import random
import discord
from typing import Optional, Dict, Literal

from translate import translations
from bot_instance import get_bot

from services.utils import hide_half_string

bot = get_bot()


def create_profile_embed(
    profile_data: Dict,
    lang: Literal["ru", "en"] = "en"
):
    category_name: Optional[str] = profile_data.get("service_category_name")
    image_url = profile_data['service_image']
    
    if isinstance(image_url, list):
        image_url = random.choice(image_url)
    if not category_name:
        category_name = profile_data['tag']
    
    description: str = profile_data['service_description']
    if len(description) >= 100:
        description = description[:95] + "..."
    embed = discord.Embed(
        title=profile_data['profile_username'],
        description=description
    )
    embed.set_image(url=image_url)
    
    embed.add_field(
        name=translations["price_field"][lang],
        value=translations["price_value"][lang].format(price=profile_data['service_price']),
        inline=True
    )
    
    embed.add_field(
        name=translations["category_field"][lang],
        value=category_name, 
        inline=True
    )
    
    if profile_data.get("profile_languages"):
        languages = ", ".join(profile_data['profile_languages']) 
        embed.add_field(
            name=translations["languages_field"][lang],
            value=languages,
            inline=False
        )
    
    return embed


def create_profile_embed_2(
    profile_data: Dict,
    lang: Literal["ru", "en"] = "en"
):
    embed = discord.Embed(
        title=profile_data['profile_username'],
        description=profile_data['service_description']
    )
    embed.set_image(url=profile_data['service_image'])
    
    embed.add_field(
        name=translations["price_field"][lang],
        value=translations["price_value"][lang].format(price=profile_data['service_price']),
        inline=True
    )
    
    embed.add_field(
        name=translations["category_field"][lang],
        value=profile_data['service_title'], 
        inline=True
    )
    
    return embed


def create_boost_embed(
    profile_data: Dict,
    amount: float,
    lang: Literal["ru", "en"] = "en"
):
    image_url = profile_data['service_image']  
    if isinstance(image_url, list):
        image_url = random.choice(image_url)       
    embed = discord.Embed(
        title=profile_data['profile_username'],
        description=translations["boost_question"][lang].format(
            amount=amount,
            username=profile_data["discord_username"]
        )
    )
    embed.set_image(url=image_url)
    return embed


def _build_embed_message_order(
    services_db,
    extra_text: str,
    lang: str,
    guild_id: int,
    customer: discord.User = None
) -> str:
    service_title = services_db.app_choice
    if not service_title:
        service_title = "All players"
    sex = services_db.sex_choice
    if not sex:
        sex = "Male/Female"
    language = services_db.language_choice
    if not language:
        language = "ALL"
    server = services_db.server_choice
    if not server:
        server = "Все" if lang == "ru" else "All"

    guild = bot.get_guild(guild_id)
    if customer:
        customer_discord_id: str = hide_half_string(str(customer.id))
    else:
        customer_discord_id: str = translations["order_from_webapp"][lang],
    embed = discord.Embed(
        title=translations["order_alert_title"][lang],
        description=translations["order_new_alert_new"][lang].format(
            customer_discord_id=customer_discord_id,
            choice=service_title,
            server_name=guild.name,
            language=language,
            gender=sex.capitalize(),
            game_server=server,
            extra_text=extra_text if extra_text else ""
        ),
        color=discord.Color.blue()
    )
    return embed
