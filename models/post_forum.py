from typing import Union, List
import discord

from translate import get_lang_prefix, translations

from database.dto.sql_forum_posted import ForumUserPostDatabase
from message_constructors import create_profile_embed
from serializers.profile_serializer import serialize_profile_data
from services.logger.client import CustomLogger
from views.order_access_reject_view import OrderPlayView

logger = CustomLogger


class Post_FORUM:
    def __init__(self, bot, profile_data, forum_channel, thread=False):
        self.bot = bot
        self.forum_channel: discord.ForumChannel = forum_channel
        self.forum_id: int = forum_channel.id
        self.guild_id: int = str(forum_channel.guild.id)
        self.profile_data: dict = serialize_profile_data(profile_data)
        self.thread: Union[discord.Thread, bool] = thread
        self.lang = get_lang_prefix(int(self.guild_id))

    async def _create_new_tag(self, tag_name: str) -> discord.ForumTag:
        new_tags = list(self.forum_channel.available_tags)
        new_tag = discord.ForumTag(name=tag_name)
        new_tags.append(new_tag)
        try:
            await self.forum_channel.edit(available_tags=new_tags)
        except discord.DiscordException:
            await logger.error_discord(
                f"Tag: {tag_name} already has in {self.guild_id}! {new_tag in self.forum_channel.available_tags}"
            )

    async def _get_tags(self) -> List[discord.ForumTag]:
        tag_name: str = self.profile_data["tag"]
        languages: List[str] = self.profile_data["profile_languages"] or []
        gender: str = self.profile_data["profile_gender"] or "OTHER"
        gender_list: List[str] = [gender] if gender != "OTHER" else ["Male", "Female"]
        tags: List[discord.ForumTag] = [] 
        for forum_tag in self.forum_channel.available_tags:
            if (
                forum_tag.name.lower() == tag_name.lower()
            ) or (
                forum_tag.name.lower() in [i.lower() for i in languages]
            ) or (
                forum_tag.name.lower() in [i.lower() for i in gender_list]
            ):
                tags.append(forum_tag)
        return tags

    async def post_user_profile(self):
        username: str = self.profile_data['profile_username']

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

        tags: List[discord.ForumTag] = await self._get_tags()

        if self.thread:
            first_message = await self.thread.fetch_message(self.thread.id)
            await first_message.edit(embed=embed)
        else:
            thread_result = await self.forum_channel.create_thread(
                name=translations["profile_thread_name"][self.lang].format(username=username),
                content=translations["interaction_prompt"][self.lang],
                embed=embed,
                reason="Automated individual profile showcase",
                applied_tags=tags,
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
