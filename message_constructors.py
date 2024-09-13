from typing import Optional, Dict
import discord


def create_profile_embed(profile_data: Dict):
    category_name: Optional[str] = profile_data.get("service_category_name")
    if not category_name:
        category_name = profile_data['service_type_name']
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    embed.set_image(url=profile_data['service_image'])
    embed.add_field(name="Price", value=f"${profile_data['service_price']} /hour", inline=True)
    embed.add_field(name="Category", value=f"{category_name}", inline=True)
    return embed

def create_profile_embed_2(profile_data):
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    embed.set_image(url=profile_data['service_image'])
    embed.add_field(name="Price", value=f"${profile_data['service_price']} /hour", inline=True)
    embed.add_field(name="Category", value=f"{profile_data['service_title']}", inline=True)
    return embed
