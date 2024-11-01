import asyncio
from gettext import translation
from bot_instance import get_bot
from database.dto.psql_services import Services_Database
import discord
from discord.ext import commands, tasks
from discord import Embed
import json
from config import INVITE_LOGS_CHANNEL_ID, MAIN_GUILD_ID
from services.sqs_client import SQSClient
from translate import get_lang_prefix

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

        if await self._is_user_already_invited(member.id):
            return

        lang = get_lang_prefix(member.guild.id)
        logs = self.bot.get_channel(int(self.logs_channel))
        embed = self._create_member_embed(member)

        await asyncio.sleep(2)  # Delay to ensure invites are updated
        try:
            used_invite = await self._identify_used_invite(member.guild)
            inviter = self._get_inviter_from_invite(used_invite)

            if used_invite and inviter:
                await self._process_invite_reward(inviter, member, used_invite, lang, embed)
                await logs.send(embed=embed)
            else:
                self._add_unknown_invite_info(embed)

        except Exception as e:
            self._add_error_info(embed, f"Error tracking invite on member join: {e}")


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if await self._is_bot_already_added(guild.id):
            return

        try:
            logs = self.bot.get_channel(int(INVITE_LOGS_CHANNEL_ID))

            await asyncio.sleep(4)  # Delay for audit log processing

            inviter = await self._get_bot_inviter(guild)

            if inviter:
                if guild.member_count >= 100:
                    await self._process_bot_integration_reward(inviter, guild, logs)
                else:
                    await inviter.send("The SideKick bot has been added to your server. You will receive 1000 points only for adding Sidekick to servers where member count reaches 100 members")
            else:
                print(f"Couldn't find the inviter for {guild.name}")
        except Exception as e:
            print(f"Error loading invites for new guild {guild.name}: {e}")


    async def _is_user_already_invited(self, member_id):
        return await self.services_db.check_if_user_already_been_invited(invited_discord_id=member_id)

    def _create_member_embed(self, member):
        embed = Embed(description="Just joined the server", color=0x03d692)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_footer(text="ID: " + str(member.id))
        embed.timestamp = member.joined_at
        return embed

    async def _identify_used_invite(self, guild):
        invites_before = self.invites[guild.id]
        invites_after = await guild.invites()
        self.invites[guild.id] = invites_after

        for invite in invites_before:
            updated_invite = self.find_invite_by_code(invites_after, invite.code)
            if updated_invite and invite.uses < updated_invite.uses:
                return updated_invite
        return None

    def _get_inviter_from_invite(self, used_invite):
        return self.manual_invites.get(used_invite.code, used_invite.inviter) if used_invite else None

    async def _process_invite_reward(self, inviter, member, used_invite, lang, embed):
        embed.add_field(
            name="Used invite",
            value=f"Inviter: {inviter.mention} (`{inviter}` | `{inviter.id}`)\n"
                f"Code: `{used_invite.code}`\nUses: `{used_invite.uses}`\nPoints: 100",
            inline=False
        )

        await self._send_reward_message(inviter, member, used_invite, lang)
        await self.services_db.save_user_reward(
            discord_id=inviter.id, reward_type="DISCORD_INVITE", server_id=0, invited_discord_id=member.id
        )

    async def _send_reward_message(self, inviter, member, used_invite, lang):
        sqs = SQSClient()
        sqs.send_task_records_message(discord_id=inviter.id, type="DISCORD_INVITE")

        if await self.services_db.check_if_user_rewarded(discord_id=inviter.id, reward_type="DISCORD_INVITE", server_id=0, invited_discord_id=member.id):
            await inviter.send(translation["invite_already_rewarded"][lang])
        else:
            await inviter.send(
                f"{member.name} has been invited to the SideKick server with your invite link: https://discord.gg/{used_invite.code} and you've gained 100 points.\n"
                "Check out https://app.sidekick.fans/tasks or use the /points command."
            )

    def _add_unknown_invite_info(self, embed):
        embed.add_field(
            name="Used invite",
            value="Invite details could not be retrieved. Please check manually.",
            inline=False
        )

    def _add_error_info(self, embed, message):
        embed.add_field(name="Error", value=message, inline=False)

    async def _is_bot_already_added(self, guild_id):
        return await self.services_db.check_if_bot_already_added(server_id=guild_id)

    async def _get_bot_inviter(self, guild):
        inviter = None
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            inviter = entry.user
        return inviter

    async def _process_bot_integration_reward(self, inviter, guild, logs):
        if await self.services_db.check_if_user_rewarded(discord_id=inviter.id, reward_type="DISCORD_BOT_INTEGRATION", server_id=guild.id, invited_discord_id=0):
            await inviter.send("You have already been rewarded for adding the SideKick bot to this server.")
        else:
            await self._send_bot_integration_reward(inviter, guild, logs)

    async def _send_bot_integration_reward(self, inviter, guild, logs):
        embed = discord.Embed(
            title="Bot Added to Server",
            description=f"The SideKick App has just been added to the server {guild.name} successfully and you’ve gained 1000 points.\n"
                        "Check out https://app.sidekick.fans/tasks or with the /points command.",
            color=discord.Color.blue()
        )
        await inviter.send(embed=embed)

        logs_embed = discord.Embed(
            title="Bot Added to Server",
            description=f"The SideKick App has just been added to the server {guild.name}.\n"
                        f"Inviter: {inviter.mention} (`{inviter}` | `{inviter.id}`)\nPoints: 1000",
            color=discord.Color.blue()
        )
        await logs.send(embed=logs_embed)

        sqs = SQSClient()
        sqs.send_task_records_message(discord_id=inviter.id, type="DISCORD_BOT_INTEGRATION")

        await self.services_db.save_user_reward(discord_id=inviter.id, reward_type="DISCORD_BOT_INTEGRATION", server_id=guild.id, invited_discord_id=0)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            self.invites.pop(guild.id)
        except KeyError:
            pass

