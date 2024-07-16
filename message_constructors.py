import discord

def create_profile_embed(profile_data):
    # Create the embed with the user's name and about section
    print("The passed profile data: ", profile_data)
    embed = discord.Embed(title=profile_data['profileUsername'], description=profile_data['serviceDescription'])
    # Set the image to the user's picture
    embed.set_image(url=profile_data['serviceImage'])
    # Add fields for the price and category
    embed.add_field(name="Price", value=f"${profile_data['servicePrice']}/hour", inline=True)
    embed.add_field(name="Category", value=f"{profile_data['serviceTitle']}", inline=True)
    return embed

def create_profile_embed_2(profile_data):
    # Create the embed with the user's name and about section
    print("The passed profile data: ", profile_data)
    embed = discord.Embed(title=profile_data['profile_username'], description=profile_data['service_description'])
    # Set the image to the user's picture
    embed.set_image(url=profile_data['service_image'])
    # Add fields for the price and category
    embed.add_field(name="Price", value=f"${profile_data['service_price']}/hour", inline=True)
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
