import discord

def create_profile_embed(profile_data):
    half_price = int(profile_data['servicePrice']) / 2
    embed = discord.Embed(title=profile_data['profileUsername'], description=profile_data['serviceDescription'])
    embed.set_image(url=profile_data['serviceImage'])
    embed.add_field(name="Price", value=f"~~${profile_data['servicePrice']}~~ ${half_price:.2f}/hour", inline=True)
    embed.add_field(name="Category", value=f"{profile_data['serviceTitle']}", inline=True)
    return embed

def create_profile_embed_2(profile_data):
    half_price = int(profile_data['service_price']) / 2
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    embed.set_image(url=profile_data['service_image'])
    embed.add_field(name="Price", value=f"~~${profile_data['service_price']}~~ ${half_price:.2f}/hour", inline=True)
    embed.add_field(name="Category", value=f"{profile_data['service_title']}", inline=True)
    return embed

def create_forum_embed(profile_data, category):
    embed = discord.Embed(
        title=profile_data['name'],
        description=f"Discord username: <@{int(profile_data['user_id'])}>\n\n {profile_data['about']}"
    )
    embed.set_author(name=f"@{profile_data['discord_username']}", url=f"https://discord.com/users/{profile_data['user_id']}")
    embed.set_image(url=profile_data['user_picture'])
    embed.add_field(name="Price", value=f"${profile_data['price']}/hour", inline=True)
    embed.add_field(name="Category", value=profile_data.get('category', f'{category}'), inline=True)
    return embed