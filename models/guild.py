from config import MAIN_GUILD_ID

from bot_instance import get_bot

bot = get_bot()


async def is_member_of_main_guild(user_id):
    main_guild = bot.get_guild(MAIN_GUILD_ID)
    if main_guild is None:
        return False
    member = main_guild.get_member(user_id)
    return member is not None