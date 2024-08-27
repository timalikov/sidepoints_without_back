import discord

def create_profile_embed(profile_data):
    half_price = int(profile_data['service_price']) / 2
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    embed.set_image(url=profile_data['service_image'])
    embed.add_field(name="Price", value=f"~~${profile_data['service_price']}~~ ${half_price:.2f}/hour", inline=True)
    embed.add_field(name="Category", value=f"{profile_data['service_title']}", inline=True)
    return embed

def create_profile_embed_2(profile_data):
    half_price = int(profile_data['service_price']) / 2
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    embed.set_image(url=profile_data['service_image'])
    embed.add_field(name="Price", value=f"~~${profile_data['service_price']}~~ ${half_price:.2f}/hour", inline=True)
    embed.add_field(name="Category", value=f"{profile_data['service_title']}", inline=True)
    return embed
