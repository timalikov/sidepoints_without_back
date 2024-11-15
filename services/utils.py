from database.dto.psql_services import Services_Database
from bot_instance import get_bot

bot = get_bot()

def hide_half_string(text: str) -> str:
    half_len: int = int(len(text) / 2)
    return text[:-half_len] + ("#" * half_len)


async def save_user_id(user_id):
    services_db = Services_Database()
    existing_user_ids = await services_db.get_user_ids_wot_tournament()
    if user_id in existing_user_ids:
        return
    else:
        await services_db.save_user_wot_tournament(user_id)
    

async def get_guild_invite_link(guild_id):
    guild = bot.get_guild(guild_id)
    if guild:
        invite = "https://discord.gg/sidekick"  # Expires in 1 day, 1 use
        return invite
    return None
