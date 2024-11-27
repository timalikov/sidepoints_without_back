from typing import Dict, Callable
import requests

from services.logger.client import CustomLogger

logger = CustomLogger


async def _handle_500(response: requests.Response) -> dict:
    await logger.http_error("Unknown error", response)
    return False


async def _handle_400(response: requests.Response) -> dict:
    await logger.http_warning("GET WALLET", response)
    return False


async def _handle_404(response: requests.Response) -> dict:
    await logger.http_warning("GET WALLET", response)
    return False


async def _handle_200(response: requests.Response) -> dict:
    await logger.http_warning("GET WALLET", response)
    return True


async def handle_status_code(response: requests.Response) -> bool:
    methods: Dict[int, Callable] = {
        500: _handle_500,
        400: _handle_400,
        404: _handle_404,
        200: _handle_200
    }
    handle = methods.get(response.status_code)
    if handle:
        return await handle(response)
    return False

