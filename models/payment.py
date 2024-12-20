from typing import Dict, Optional, Tuple
from decimal import Decimal
import discord
import requests

from config import (
    JWT_AUTH_PASSWORD,
    JWT_AUTH_URL,
    PAYMENT_LINK,
    SERVER_WALLET_URL,
    BOOST_URL,
    GUIDE_CATEGORY_NAME,
    GUIDE_CHANNEL_NAME,
    BECOME_CATEGORY_NAME,
    BECOME_CHANNEL_NAME,
    MAIN_GUILD_ID,
    FREE_TOP_UP_URL,
    FREE_TOP_UP_TOKEN,
)
from bot_instance import get_bot

from services.logger.client import CustomLogger
from services.common_http import handle_status_code
from web3_interaction.balance_checker import get_usdt_balance
from models.enums import PaymentStatusCode
from models.public_channel import get_or_create_channel_by_category_and_name
from models.kicker_service import build_service_price

logger = CustomLogger
bot = get_bot()


async def create_wallet(user_id: int) -> requests.Response:
    return requests.post(SERVER_WALLET_URL + "/create", json={"userId": str(user_id)})


async def find_wallet(user_id: int) -> requests.Response:
    return requests.get(SERVER_WALLET_URL + f"/find?userId={user_id}")


async def is_wallet_exist_by_discord_id(user_id: int) -> bool:
    exists_response = requests.get(SERVER_WALLET_URL + f"/exists?userId={user_id}")
    is_exists = exists_response.json().get("exists")
    return is_exists


async def top_up_free_ten_usdt(user: discord.User, amount: int) -> None:
    response: requests.Response = await create_wallet(user.id)
    success = await handle_status_code(response)
    if not success:
        return PaymentStatusCode.SERVER_PROBLEM
    response_data = response.json()
    sender_address: str = response_data["address"]
    response = requests.post(
        url=FREE_TOP_UP_URL, 
        headers={"Content-Type": "application/json", "X-API-Token": FREE_TOP_UP_TOKEN},
        json={"message": "send_transaction", "to_address": sender_address, "amount": str(amount)}
    )
    top_up_success = await handle_status_code(response)
    if top_up_success:
        order_lobby_channel = await get_or_create_channel_by_category_and_name(
            category_name=GUIDE_CATEGORY_NAME,
            channel_name=GUIDE_CHANNEL_NAME,
            guild=bot.get_guild(MAIN_GUILD_ID)
        )
        become_channel = await get_or_create_channel_by_category_and_name(
            category_name=BECOME_CATEGORY_NAME,
            channel_name=BECOME_CHANNEL_NAME,
            guild=bot.get_guild(MAIN_GUILD_ID)
        )
        user_embed = discord.Embed(
            title="Thanks for you using /Order command",
            description=(
                "Here is 10$ bonus 💵 for fist order free. and all the kickers price are 6$ now!!\n"
                f"In {order_lobby_channel.jump_url} use the /order command to Get 10$\n"
                "```Command Info: \n\n"
                "/find  +@discord name   :find a kicker\n\n"
                "/order :place an order\n\n"
                "/boost  +@discord name+anount  : boost a kicker\n\n"
                "/wallet :Top Up```\n\n"
                f"*In {order_lobby_channel.jump_url} use the /order command to Get 10$, in {become_channel.jump_url}  to sign up as a kicker*\n"
                "10 USD will be in your wallet in just a second! Use the /wallet command to check it out!"
            ),
            colour=discord.Colour.green()
        )
        user_embed.set_image(url="https://discord-photos.s3.eu-central-1.amazonaws.com/sidekick-back-media/discord_bot/free_poster.png")
        await user.send(embed=user_embed)


async def get_server_wallet_by_discord_id(user_id: int) -> str:
    is_exists = await is_wallet_exist_by_discord_id(user_id)
    if is_exists:
        response = await find_wallet(user_id)
    else:
        response = await create_wallet(user_id)
    is_success = await handle_status_code(response=response)
    if not is_success:
        return None
    data: Dict = response.json()
    return data["address"]


async def get_usdt_balance_by_discord_user(user: discord.User) -> float:
    user_wallet: str = await get_server_wallet_by_discord_id(user.id)
    if not user_wallet:
        return 0
    user_balance: Decimal = get_usdt_balance(user_wallet)
    return user_balance


async def check_user_wallet(user: discord.User, amount: float) -> PaymentStatusCode:
    user_balance: Decimal = await get_usdt_balance_by_discord_user(user)
    if isinstance(user_balance, str):
        return PaymentStatusCode.OPBNB_PROBLEM
    if user_balance < amount:
        return PaymentStatusCode.NOT_ENOUGH_MONEY
    return PaymentStatusCode.SUCCESS


async def check_user_wallet_payment(user: discord.User, target_service: Dict) -> PaymentStatusCode:
    return await check_user_wallet(user=user, amount=target_service["service_price"])


def get_jwt_token(user: discord.User) -> str:
    request_json = {
        "userId": str(user.id),
        "password": JWT_AUTH_PASSWORD
    }
    jwt_response = requests.post(
        url=JWT_AUTH_URL, json=request_json
    )
    if jwt_response.status_code != 200:
        logger.http_error_sync(
            place="JWT", response=jwt_response
        )
        return
    return jwt_response.json().get("token")


async def send_payment(
    user: discord.User,
    target_service: Dict,
    discord_server_id: int,
    coupon: Optional[Dict] = None
) -> Tuple[PaymentStatusCode, Optional[int]]:
    service_price = build_service_price(target_service, coupon)
    status_check = await check_user_wallet(user=user, amount=service_price)
    if status_check != PaymentStatusCode.SUCCESS:
        logger.error(f"User id: {user.id} || Message: {status_check.name}")
        return status_check, None
    token: str = get_jwt_token(user)
    headers: Dict = {"Authorization": f"Bearer {token}"}
    payment_json = {
        "discordServerId": str(discord_server_id),
        "serviceId": str(target_service["service_id"]),
        "useCustodial": True
    }
    if coupon:
        payment_json["couponId"] = coupon["id"]
    payment_response = requests.post(
        url=PAYMENT_LINK,
        headers=headers,
        json=payment_json
    )
    success = await handle_status_code(payment_response)
    if not success:
        return PaymentStatusCode.SERVER_PROBLEM, None
    return PaymentStatusCode.SUCCESS, payment_response.json().get("id")


async def send_boost(user: discord.User, target_service: Dict, amount: int) -> PaymentStatusCode:
    status_check = await check_user_wallet(user, amount)
    if status_check != PaymentStatusCode.SUCCESS:
        logger.error(f"User id: {user.id} || Message: {status_check.name}")
        return status_check
    token: str = get_jwt_token(user)
    headers: Dict = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        BOOST_URL,
        headers=headers,
        json={
            "boostedId": str(target_service["profile_id"]),
            "amount": amount
        }
    )
    success = await handle_status_code(response)
    if success:
        return PaymentStatusCode.SUCCESS
    return PaymentStatusCode.SERVER_PROBLEM