import discord

from logging import getLogger

from bot_instance import get_bot
from config import LOGGER_DISCORD_USERS_LOGS, LOGGER_SEND_DISCORD_DM_LOGS

from requests import Response

logger = getLogger("")
bot = get_bot()


class CustomLogger:
    """
    Custom class for logging data!
    """

    @staticmethod
    async def http_discord(
        place: str,
        response: Response
    ) -> None:
        test_embed = discord.Embed(
            title="Backend response",
            colour=discord.Colour.red()
        )
        test_embed.add_field(name="WHERE", value=place)
        test_embed.add_field(name="Status code", value=response.status_code)
        test_embed.add_field(name="Message", value=response.text)
        test_embed.add_field(name="Request body", value=response.request.body)
        for user_id in LOGGER_DISCORD_USERS_LOGS:
            user = bot.get_user(user_id)
            if not user:
                continue
            await user.send(embed=test_embed)

    @staticmethod
    def _get_http_message(
        place: str,
        response: Response
    ) -> None:
        return (
            f"- Place: {place} || Status: {response.status_code}\n"
            f"- Message: {response.text}\n"
            f"- URL: {response.url}\n"
            f"- Body: {response.request.body.decode() if response.request.body else ''}\n"
            "========================="
        )
    
    @staticmethod
    async def http_error(
        place: str,
        response: Response
    ) -> None:
        if LOGGER_SEND_DISCORD_DM_LOGS:
            await CustomLogger.http_discord(place, response)
        logger.error(
            CustomLogger._get_http_message(
                place=place,
                response=response,
            )
        )
    
    @staticmethod
    async def http_warning(
        place: str,
        response: Response
    ) -> None:
        if LOGGER_SEND_DISCORD_DM_LOGS:
            await CustomLogger.http_discord(place, response)
        logger.warning(
            CustomLogger._get_http_message(
                place=place,
                response=response,
            )
        )

    @staticmethod
    async def http_error_sync(
        place: str,
        response: Response
    ) -> None:
        logger.error(
            CustomLogger._get_http_message(
                place=place,
                response=response,
            )
        )
    
    @staticmethod
    async def http_warning_sync(
        place: str,
        response: Response
    ) -> None:
        logger.warning(
            CustomLogger._get_http_message(
                place=place,
                response=response,
            )
        )

    @staticmethod
    def error(message: str) -> None:
        logger.error(message)

    @staticmethod
    def warning(message: str) -> None:
        logger.warning(message)
