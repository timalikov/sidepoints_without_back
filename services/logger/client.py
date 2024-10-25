from logging import getLogger

from requests import Response

logger = getLogger("")

class CustomLogger:
    """
    Custom class for logging data!
    """

    @staticmethod
    def _get_http_message(
        place: str,
        response: Response
    ) -> None:
        return (
            f"- Place: {place} || Status: {response.status_code}\n"
            f"- Message: {response.text}\n"
            f"- URL: {response.url}\n"
            f"- Body: {response.request.body.decode()}\n"
            "========================="
        )
    
    @staticmethod
    def http_error(
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
    def http_warning(
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
