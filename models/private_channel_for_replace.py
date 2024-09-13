from config import CUSTOMER_SUPPORT_TEAM_IDS
import discord

async def create_channel_for_replace(bot, guild_id, customer, base_category_name = "Sidekick Customer Support"):
    guild = bot.get_guild(guild_id)
    channel_name = f"Kicker replacement - {customer.name}"


    category = None
    index = 1
    while not category:
        category_name = f"{base_category_name}{index}"
        category = discord.utils.get(guild.categories, name=category_name)
        if category and len(category.channels) >= 50:
            category = None
            index += 1
        elif not category:
            category = await guild.create_category(category_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        customer: discord.PermissionOverwrite(read_messages=True),
    }
    for cs_id in CUSTOMER_SUPPORT_TEAM_IDS:
        cs_member = guild.get_member(cs_id)
        if cs_member:
            overwrites[cs_member] = discord.PermissionOverwrite(read_messages=True)

    channel = await category.create_voice_channel(channel_name, overwrites=overwrites)

    invite = await channel.create_invite(max_age=86400)

    await channel.send(
        f"Welcome to the Sidekick kicker replace room"
    )

    return invite.url