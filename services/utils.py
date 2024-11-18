import discord
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

async def list_online_users(guild):
    if guild is None:
        return []
    online_members = [member for member in guild.members if str(member.status) == 'online']
    online_member_ids = [member.id for member in online_members]
    return online_member_ids


def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.guild is not None and interaction.guild.owner_id == interaction.user.id


def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator


async def list_all_users_with_online_status(guild):
    if guild is None:
        return []
    all_member_ids = [member.id for member in guild.members]
    return all_member_ids

