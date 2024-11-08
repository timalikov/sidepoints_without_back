import asyncio
from bot_instance import get_bot
from database.dto.psql_services import Services_Database
import discord
from discord.ext import commands, tasks
from discord import Embed
import json
from config import INVITE_LOGS_CHANNEL_ID, MAIN_GUILD_ID
from services.sqs_client import SQSClient
from translate import get_lang_prefix, translations

bot = get_bot()

class InviteTracker(commands.Cog):
    """
    Tracks invites and logs which invite was used when a member joins or leaves the server.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logs_channel = INVITE_LOGS_CHANNEL_ID
        self.invites = {}
        self.manual_invites = {}
        self.refresh_invites.start() 
        self.services_db = Services_Database()

    @tasks.loop(seconds=4)  
    async def refresh_invites(self):
        guild = bot.get_guild(MAIN_GUILD_ID)
        self.invites[guild.id] = await guild.invites()

    def find_invite_by_code(self, invite_list, code):
        for invite in invite_list:
            if invite.code == code:
                return invite
            
    @commands.Cog.listener()
    async def on_member_join(self, member):

        if member.guild.id != MAIN_GUILD_ID:
            return
        
        lang = get_lang_prefix(member.guild.id)
     

        logs = self.bot.get_channel(int(self.logs_channel))
        embed = Embed(description=translations["first_join"][lang], color=0x03d692)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_footer(text="ID: " + str(member.id))
        embed.timestamp = member.joined_at

        await asyncio.sleep(2)

        try:
            invites_before = self.invites[member.guild.id]
            invites_after = await member.guild.invites()
            self.invites[member.guild.id] = invites_after

            used_invite = None
            for invite in invites_before:
                updated_invite = self.find_invite_by_code(invites_after, invite.code)
                if updated_invite and invite.uses < updated_invite.uses:
                    used_invite = updated_invite
                    break

            if used_invite:
                inviter = self.manual_invites.get(used_invite.code, used_invite.inviter)

                if_user_already_invited = await self.services_db.check_if_user_already_been_invited(invited_discord_id=member.id)
                if if_user_already_invited:
                    await inviter.send(translations["already_invited"][lang].format(member_name=member.name))
                    return
                
                embed.add_field(
                    name=translations["used_invited"][lang],
                    value=translations["invited_user_point"][lang].format(
                        inviter_mention=inviter.mention,
                        inviter=inviter,
                        inviter_id=inviter.id,
                        code=used_invite.code,
                        uses=used_invite.uses
                    ),
                    inline=False
                )
                
                sqs = SQSClient()
                sqs.send_task_records_message(discord_id=inviter.id, type="DISCORD_INVITE")

                is_user_rewarded = await self.services_db.check_if_user_rewarded(discord_id=inviter.id, reward_type="DISCORD_INVITE", server_id=0, invited_discord_id=member.id)
                if is_user_rewarded:
                    await inviter.send(translations["invite_already_rewarded"][lang])
                    return
                else:
                    await inviter.send(translations["link_invite_message"][lang].format(member_name=member.name,used_invite_code=used_invite.code))
                    await self.services_db.save_user_reward(discord_id=inviter.id, reward_type="DISCORD_INVITE", server_id=0, invited_discord_id=member.id)
                
                await logs.send(embed=embed)
            
                
            else:
                embed.add_field(
                    name=translations["task_records_name"][lang],
                    value=translations["task_records_value"][lang],
                    inline=False
                )

        except Exception as e:
            print(f"Error tracking invite on member join: {e}")
            embed.add_field(
                name=translations["task_records_error_name"][lang],
                value=translations ["task_records_error_value"][lang],
                inline=False
            )


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        lang = get_lang_prefix(guild.id)
        try:
            logs = bot.get_channel(int(INVITE_LOGS_CHANNEL_ID))

            await asyncio.sleep(5)

            inviter = None
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                inviter = entry.user

            if inviter:
                if guild.member_count < 100:
                    await inviter.send(translations["guild_join_inviter"][lang])
                    return
                if_bot_already_added = await self.services_db.check_if_bot_already_added(server_id=guild.id)
                if if_bot_already_added:
                    await inviter.send(translations["guild_bot_is_added"][lang])
                    return
                is_user_rewarded = await self.services_db.check_if_user_rewarded(discord_id=inviter.id, reward_type="DISCORD_BOT_INTEGRATION", server_id=guild.id, invited_discord_id=0)
                if is_user_rewarded:
                    await inviter.send(translations["guild_reward_adding"][lang])
                    return
                else:
                    embed = discord.Embed(
                        title=translations["guild_bot_added_title"][lang],
                        description=translations["guild_sidekick_app_added"][lang].format(guild_name=guild.name),
                        color=discord.Color.blue()
                    )

                    await inviter.send(embed=embed)

                    logs_embed = discord.Embed(
                        title=translations["guild_sidekick_app_added_full_title"][lang],
                        description=translations["guild_sidekick_app_added_full"][lang]
                        .format(guild_name=guild.name,inviter_mention=inviter.mention,inviter=inviter,inviter_id=inviter.id),
                        color=discord.Color.blue()
                    )
                    
                    await logs.send(embed=logs_embed)

                    sqs = SQSClient()
                    sqs.send_task_records_message(discord_id=inviter.id, type="DISCORD_BOT_INTEGRATION")

                    await self.services_db.save_user_reward(discord_id=inviter.id, reward_type="DISCORD_BOT_INTEGRATION", server_id=guild.id, invited_discord_id=0)
            else:
                print(f"Couldn't find the inviter for {guild.name}")
        except Exception as e:
            print(f"Error loading invites for new guild {guild.name}: {e}")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            self.invites.pop(guild.id)
        except KeyError:
            pass
