import asyncio
from bot_instance import get_bot
import discord
from discord.ext import commands
from discord import Embed
import json
from config import LOGS_CHANNEL_ID

bot = get_bot()

class InviteTracker(commands.Cog):
    """
    Tracks invites and logs which invite was used when a member joins or leaves the server.
    """
    def __init__(self, bot):
        self.bot = bot
        self.logs_channel = LOGS_CHANNEL_ID
        self.invites = {}
        bot.loop.create_task(self.load_invites())

    async def load_invites(self):
        # Wait until the bot is ready
        await self.bot.wait_until_ready()
        # Load invites for all guilds the bot is part of
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = await guild.invites()
            except Exception as e:
                print(f"Failed to load invites for {guild.name}: {e}")

    def find_invite_by_code(self, invite_list, code):
        for invite in invite_list:
            if invite.code == code:
                return invite

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logs = self.bot.get_channel(int(self.logs_channel))
        embed = Embed(description="Just joined the server", color=0x03d692)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_footer(text="ID: " + str(member.id))
        embed.timestamp = member.joined_at

        asyncio.sleep(2)

        try:
            invites_before = self.invites[member.guild.id]
            invites_after = await member.guild.invites()
            self.invites[member.guild.id] = invites_after

            for invite in invites_before:
                print("invite tracker ")
                print(invite.code, invite.uses)
                if invite.uses < self.find_invite_by_code(invites_after, invite.code).uses:
                    embed.add_field(
                        name="Used invite",
                        value=f"Inviter: {invite.inviter.mention} (`{invite.inviter}` | `{invite.inviter.id}`)\n"
                              f"Code: `{invite.code}`\n"
                              f"Uses: `{invite.uses}`",
                        inline=False
                    )
                    break

        except Exception as e:
            print(f"Error tracking invite on member join: {e}")

        await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"Joined {guild.name}")
        try:
            self.invites[guild.id] = await guild.invites()
            logs = bot.get_channel(int(LOGS_CHANNEL_ID))

            await asyncio.sleep(5)
            if guild.member_count > 1:
                print("member count = ", guild.member_count)

            inviter = None
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                inviter = entry.user

            if inviter:
                print(f"The bot was added to {guild.name} by {inviter.name}#{inviter.discriminator}")
                await inviter.send(f"The SideKick server has been added to server {guild.name} successfully and you’ve gained 1000 points. Check out https://app.sidekick.fans/tasks.")
                await logs.send(f"The bot was added to {guild.name} by {inviter.name}#{inviter.discriminator}")

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

