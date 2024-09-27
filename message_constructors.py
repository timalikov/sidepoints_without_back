import random
from typing import Optional, Dict
import discord


def create_profile_embed(profile_data: Dict):
    category_name: Optional[str] = profile_data.get("service_category_name")
    image_url = profile_data['service_image']
    if isinstance(image_url, list):
        image_url = random.choice(image_url)
    if not category_name:
        category_name = profile_data['service_type_name']
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    embed.set_image(url=image_url)
    embed.add_field(name="Price", value=f"${profile_data['service_price']} /hour", inline=True)
    embed.add_field(name="Category", value=category_name, inline=True)
    if profile_data.get("profile_languages"):
        languages = ", ".join(profile_data['profile_languages']) 
        embed.add_field(name="Languages", value=languages, inline=False)
    return embed

def create_profile_embed_2(profile_data):
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    embed.set_image(url=profile_data['service_image'])
    embed.add_field(name="Price", value=f"${profile_data['service_price']} /hour", inline=True)
    embed.add_field(name="Category", value=f"{profile_data['service_title']}", inline=True)
    return embed
