from typing import Tuple, Dict
from decimal import Decimal
import discord
import requests

from config import (
    JWT_AUTH_PASSWORD,
    JWT_AUTH_URL,
    PAYMENT_LINK,
)

from database.dto.psql_discord_profiles import DiscordProfilesDTO
from services.logger.client import CustomLogger
from web3_interaction.balance_checker import get_usdt_balance
from models.enums import PaymentStatusCodes

logger = CustomLogger


async def get_usdt_balance_by_discord_user(user: discord.User) -> float:
    dto = DiscordProfilesDTO()
    user_wallet: str = await dto.get_wallet_by_discord_id(user.id)
    user_balance: Decimal = get_usdt_balance(user_wallet)
    return user_balance


async def check_user_wallet(user: discord.User, target_service: Dict) -> PaymentStatusCodes:
    user_balance: Decimal = await get_usdt_balance_by_discord_user(user)
    if isinstance(user_balance, str):
        return PaymentStatusCodes.OPBNB_PROBLEM
    if user_balance < target_service["service_price"]:
        return PaymentStatusCodes.NOT_ENOUGH_MONEY
    return PaymentStatusCodes.SUCCESS


async def get_jwt_token(user: discord.User) -> str:
    request_json = {
        "userId": str(user.id),
        "password": JWT_AUTH_PASSWORD
    }
    jwt_response = requests.post(
        url=JWT_AUTH_URL, json=request_json
    )
    if jwt_response.status_code != 200:
        logger.http_error(
            place="JWT", response=jwt_response
        )
        return
    return jwt_response.json().get("token")


async def send_payment(user: discord.User, target_service: Dict, discord_server_id: int) -> PaymentStatusCodes:
    status_check = await check_user_wallet(user, target_service)
    if status_check != PaymentStatusCodes.SUCCESS:
        logger.error(f"User id: {user.id} || Message: {status_check.name}")
        return status_check
    token: str = await get_jwt_token(user)
    headers: Dict = {"Authorization": f"Bearer {token}"}
    payment_json = {
        "discordServerId": str(discord_server_id),
        "serviceId": str(target_service["service_id"]),
        "useCustodial": True
    }
    payment_response = requests.post(
        url=PAYMENT_LINK,
        headers=headers,
        json=payment_json
    )
    if payment_response.status_code != 200:
        logger.http_error(
            place="Payment", response=payment_response
        )
        return PaymentStatusCodes.SERVER_PROBLEM
    logger.warning(payment_response.text)
    return PaymentStatusCodes.SUCCESS