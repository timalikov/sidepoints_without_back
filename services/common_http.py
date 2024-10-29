import requests

from config import (
    JWT_AUTH_PASSWORD,
    JWT_AUTH_URL,
    PAYMENT_LINK,
    SERVER_WALLET_URL
)


async def _handle_status_code(response: requests.Response) -> dict:
    ...
