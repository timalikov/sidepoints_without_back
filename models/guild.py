from config import MAIN_GUILD_ID, GUILDS_FOR_TASKS

from bot_instance import get_bot

bot = get_bot()


async def is_member_of_main_guild(user_id):
    for guild_id in GUILDS_FOR_TASKS:
        guild = bot.get_guild(guild_id)
        if not guild:
            continue
        member = guild.get_member(user_id)
        if member:
            return member
    return None