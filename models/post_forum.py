from typing import Union
import os
import discord

from button_constructors import ShareButton, ChatButton
from database.dto.sql_forum_posted import ForumUserPostDatabase
from serializers.profile_serializer import serialize_profile_data


class UserProfileView(discord.ui.View):
    def __init__(self, user_data):
        super().__init__(timeout=None)
        self.profile_data = serialize_profile_data(user_data)
        self.user_id = user_data['discord_id']
        self.task_id = user_data['service_type_id']
        button = discord.ui.Button(label="Go", style=discord.ButtonStyle.primary, custom_id=f"go_{self.user_id}")
        button.callback = self.button_callback  # Set the callback for the button
        self.add_item(button)  # Add the button to the view
        self.add_item(ShareButton(self.user_id))
        self.add_item(ChatButton(self.user_id))

    async def button_callback(self, interaction: discord.Interaction):
        print("ENTER")
        serviceId = self.profile_data['service_id']
        discordServerId = interaction.guild.id
        payment_link = f"{os.getenv('WEB_APP_URL')}/payment/{serviceId}?discordServerId={discordServerId}"
        try:
            await interaction.response.send_message(
                f"To participate in this session, please complete your payment here: {payment_link}",
                ephemeral=True
            )
        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                f"To participate in this session, please complete your payment here: {payment_link}",
                ephemeral=True
            )
        except discord.errors.HTTPException as e:
            print(f"HTTPException: {e}")
        except Exception as e:
            print(f"Unhandled exception: {e}")


class Post_FORUM:
    def __init__(self, bot, profile_data, forum_channel, thread=False):
        self.bot = bot
        self.forum_channel: discord.ForumChannel = forum_channel
        self.forum_id: int = forum_channel.id
        self.guild_id: int = str(forum_channel.guild.id)
        self.profile_data: dict = serialize_profile_data(profile_data)
        self.thread: Union[discord.Thread, bool] = thread

    async def post_user_profile(self):
        tag_name: str = self.profile_data["service_type_name"]
        username: str = self.profile_data['profile_username']
        service_id: str = self.profile_data['service_id']
        invite_link: str = f"https://app.sidekick.fans/payment/{service_id}?discordServerId={self.guild_id}"
        link_message = f"To initiate a session with {username}, please click on the link: {invite_link}"

        embed = discord.Embed(
            title=username,
            description=f"Discord username: <@{int(self.profile_data['discord_id'])}>\n\n {self.profile_data['service_description']}"
        )

        embed.set_image(url=self.profile_data['service_image'])
        embed.add_field(name="Price", value=f"${self.profile_data['service_price']}/hour", inline=True)
        embed.add_field(name="Category", value=tag_name, inline=True)
        embed.add_field(name="Link", value=link_message, inline=False)

        tag = discord.utils.get(self.forum_channel.available_tags, name=tag_name)
        if not tag:
            new_tags = list(self.forum_channel.available_tags)
            new_tags.append(discord.ForumTag(name=tag_name))
            self.forum_channel.edit(available_tags=new_tags)

        if self.thread:
            first_message = await self.thread.fetch_message(self.thread.id)
            await first_message.edit(embed=embed)
        else:
            thread_result = await self.forum_channel.create_thread(
                name=f"Profile: <@{username}>",
                content="Click 'Go' to interact with this profile!",
                embed=embed,
                reason="Automated individual profile showcase",
                applied_tags=[tag] if tag else [],
                auto_archive_duration=60,
                allowed_mentions=discord.AllowedMentions.none()
            )
            thread_id = thread_result.thread.id
            await ForumUserPostDatabase.add_forum_post(
                self.forum_id,
                thread_id,
                self.profile_data['discord_id'],
                self.guild_id
            )
            return True