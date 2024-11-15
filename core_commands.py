import discord
import discord.ext
import discord.ext.commands
from logging import getLogger

from services.storage.bucket import ImageS3Bucket
from commands.boost_command import BoostCommand
from commands.find_command import FindCommand
from commands.go_command import GoCommand
from commands.leaderboard_command import LeaderboardCommand
from commands.order_command import OrderCommand
from commands.points_command import PointsCommand
from commands.profile_command import ProfileCommand
from commands.start_command import StartCommand
from commands.subscribe_command import SubscribeCommand
from commands.start_command import StartCommand
from commands.test_command import TestCommand
from commands.wallet_command import WalletCommand
from commands.forum_command import ForumCommand
from bot_instance import get_bot
from background_tasks import (
    assign_roles_to_kickers,
    delete_old_channels,
    post_user_profiles,
    create_leaderboard,
    send_random_guide_message,
    check_success_top_up_balance,
    rename_kickers,
)

from config import (
    MAIN_GUILD_ID,
    DISCORD_BOT_TOKEN,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME,
    TEST
)
from models.public_channel import (
    get_or_create_channel_by_category_and_name,
    create_all_required_channels
)
from translate import translations
from services.cogs.invite_tracker import InviteTracker  

main_guild_id: int = MAIN_GUILD_ID

bot = get_bot()
logger = getLogger("")


@bot.event
async def on_guild_join(guild: discord.Guild):
    message: str = "@everyone\n" + translations["welcome_message"]["en"].format(server_name=guild.name)
    image = await ImageS3Bucket.get_image_by_url(
        "https://discord-photos.s3.eu-central-1.amazonaws.com/sidekick-back-media/discord_bot/%3AHow+to+make+an+order.png"
    )
    channel = await get_or_create_channel_by_category_and_name(
        category_name=GUIDE_CATEGORY_NAME,
        channel_name=GUIDE_CHANNEL_NAME,
        guild=guild
    )
    try:
        await channel.send(message, file=discord.File(image, "guild_join.png"))
    except discord.DiscordException as e:
        logger.error(str(e))


async def _create_channels() -> None:
    for guild in bot.guilds:
        try:
            await create_all_required_channels(guild=guild),
        except Exception:
            continue


@bot.event
async def on_ready():
    delete_old_channels.start()
    await bot.add_cog(InviteTracker(bot))
    if TEST:
        await bot.add_cog(TestCommand(bot))
    await bot.add_cog(ForumCommand(bot))
    await bot.add_cog(GoCommand(bot))
    await bot.add_cog(LeaderboardCommand(bot))
    await bot.add_cog(OrderCommand(bot))
    await bot.add_cog(PointsCommand(bot))
    await bot.add_cog(ProfileCommand(bot))
    await bot.add_cog(StartCommand(bot))
    await bot.add_cog(BoostCommand(bot))
    await bot.add_cog(SubscribeCommand(bot))
    await bot.add_cog(FindCommand(bot))
    await bot.add_cog(WalletCommand(bot))
    await _create_channels()
    rename_kickers.start()
    post_user_profiles.start()
    create_leaderboard.start()
    send_random_guide_message.start()
    check_success_top_up_balance.start()
    assign_roles_to_kickers.start()
    await bot.tree.sync()
    
    print(f"We have logged in as {bot.user}. Is test: {'Yes' if TEST else 'No'}. Bot: {bot}")


def run():
    bot.run(DISCORD_BOT_TOKEN)
