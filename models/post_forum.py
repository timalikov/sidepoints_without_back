from typing import Union
import discord

from message_constructors import create_profile_embed
from database.dto.sql_forum_posted import ForumUserPostDatabase
from serializers.profile_serializer import serialize_profile_data
from views.order_access_reject_view import OrderPlayView
from translate import get_lang_prefix, translations


class Post_FORUM:
    def __init__(self, bot, profile_data, forum_channel, thread=False):
        self.bot = bot
        self.forum_channel: discord.ForumChannel = forum_channel
        self.forum_id: int = forum_channel.id
        self.guild_id: int = str(forum_channel.guild.id)
        self.profile_data: dict = serialize_profile_data(profile_data)
        self.thread: Union[discord.Thread, bool] = thread
        self.lang = get_lang_prefix(int(self.guild_id))

    async def post_user_profile(self):
        tag_name: str = self.profile_data["tag"]
        username: str = self.profile_data['profile_username']
        service_id: str = self.profile_data['service_id']

        embed = create_profile_embed(self.profile_data, lang=self.lang)
        embed.description = translations["profile_description"][self.lang].format(
            discord_id=self.profile_data['discord_id'],
            service_description=self.profile_data['service_description']
        )
        view = OrderPlayView(
            service=self.profile_data,
            guild_id=self.guild_id,
            need_reject_button=False,
            show_boost_dropdown=True,
            lang=self.lang,
            timeout=None
        )

        tag: discord.ForumTag = None
        for forum_tag in self.forum_channel.available_tags:
            if tag_name.lower() == forum_tag.name.lower():
                tag = forum_tag
        if not tag:
            new_tags = list(self.forum_channel.available_tags)
            new_tag = discord.ForumTag(name=tag_name)
            new_tags.append(new_tag)
            try:
                await self.forum_channel.edit(available_tags=new_tags)
            except discord.DiscordException:
                print(
                    f"Tag: {tag_name} already has in {self.guild_id}! {new_tag in self.forum_channel.available_tags}"
                )

        if self.thread:
            first_message = await self.thread.fetch_message(self.thread.id)
            await first_message.edit(embed=embed)
        else:
            thread_result = await self.forum_channel.create_thread(
                name=translations["profile_thread_name"][self.lang].format(username=username),
                content=translations["interaction_prompt"][self.lang],
                embed=embed,
                reason="Automated individual profile showcase",
                applied_tags=[tag] if tag else [],
                auto_archive_duration=60,
                allowed_mentions=discord.AllowedMentions.none(),
                view=view
            )
            thread_id = thread_result.thread.id
            await ForumUserPostDatabase.add_forum_post(
                self.forum_id,
                thread_id,
                self.profile_data['discord_id'],
                self.guild_id
            )
            return True
