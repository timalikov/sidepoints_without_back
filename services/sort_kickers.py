from bot_instance import get_bot
from config import MAIN_GUILD_ID
import discord

bot = get_bot()

async def is_user_online(user_id):
    main_guild = bot.get_guild(MAIN_GUILD_ID)
    if main_guild is None:
        return False
    member = main_guild.get_member(int(user_id))
    return member is not None and member.status == discord.Status.online

async def sort_kickers(all_kickers):
    """
    Fetch all kickers and sort them by:
    1. Online kickers with profile_score >= 100.
    2. Online kickers with profile_score < 100.
    3. Offline kickers, sorted by profile_score.
    """

    online_high_score = []
    online = []
    offline = []

    for kicker in all_kickers:
        user_id = kicker['discord_id']
        score = kicker['profile_score']

        is_online = await is_user_online(user_id)

        if is_online:
            if score >= 100:
                online_high_score.append(kicker)
            else:
                online.append(kicker)
        else:
            offline.append(kicker)
    
    online_high_score.sort(key=lambda x: x['profile_score'], reverse=True)
    online.sort(key=lambda x: x['profile_score'], reverse=True)
    offline.sort(key=lambda x: x['profile_score'], reverse=True)

    return online_high_score + online + offline
