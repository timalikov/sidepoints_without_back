import asyncio
from bot_instance import get_bot
import discord
from discord.ext import commands, tasks
from discord import Embed
import json
from config import INVITE_LOGS_CHANNEL_ID, MAIN_GUILD_ID
from services.sqs_client import SQSClient

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
        
        logs = self.bot.get_channel(int(self.logs_channel))
        embed = Embed(description="Just joined the server", color=0x03d692)
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
                embed.add_field(
                    name="Used invite",
                    value=f"Inviter: {inviter.mention} (`{inviter}` | `{inviter.id}`)\n"
                        f"Code: `{used_invite.code}`\nUses: `{used_invite.uses}`\nPoints: 100",
                        inline=False
                )
                await inviter.send(
                    f"{member.name} has been invited to the SideKick server with your invite link: https://discord.gg/{used_invite.code} and you've gained 100 points.\n"
                    "Check out https://app.sidekick.fans/tasks or use the /points command."
                )

                sqs = SQSClient()
                sqs.send_task_records_message(discord_id=inviter.id, type="DISCORD_INVITE")
                
            else:
                embed.add_field(
                    name="Used invite",
                    value="Invite details could not be retrieved. Please check manually.",
                    inline=False
                )

        except Exception as e:
            print(f"Error tracking invite on member join: {e}")
            embed.add_field(
                name="Error",
                value="Failed to track invite usage.",
                inline=False
            )

        await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Joined {guild.name}")
        try:
            self.invites[guild.id] = await guild.invites()
            logs = bot.get_channel(int(INVITE_LOGS_CHANNEL_ID))

            await asyncio.sleep(5)
            if guild.member_count > 1:
                print("member count = ", guild.member_count)

            inviter = None
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                inviter = entry.user

            if inviter:
                print(f"The bot was added to {guild.name} by {inviter.name}#{inviter.discriminator}")
                embed = discord.Embed(
                    title="Bot Added to Server",
                    description=f"The SideKick App has just been added to the server {guild.name} successfully and you’ve gained 1000 points.\nCheck out https://app.sidekick.fans/tasks or with the /points command.",
                    color=discord.Color.blue()
                )
                
                await inviter.send(embed=embed)

                logs_embed = discord.Embed(
                    title="Bot Added to Server",
                    description=f"The SideKick App has just been added to the server {guild.name}.\nInviter: {inviter.mention} (`{inviter}` | `{inviter.id}`)\nPoints: 1000",
                    color=discord.Color.blue()
                )
                
                await logs.send(embed=logs_embed)

                sqs = SQSClient()
                sqs.send_task_records_message(discord_id=inviter.id, type="DISCORD_INVITE")
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

