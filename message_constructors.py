import random
from typing import Optional, Dict, Literal
import discord
from translate import translations


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
        
    embed = discord.Embed(
        title=profile_data['profile_username'],
        description=profile_data['service_description']
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
