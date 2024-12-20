from typing import Dict, Tuple
import requests
import discord

from config import (
    COUPON_URL,
    COUPON_ADD_URL,
)

from services.common_http import handle_status_code
from models.payment import get_jwt_token
from models.enums import HttpStatusCode, CouponAddMessage


"""
Coupon fields:
    id: UUID
    type: Enum[CouponType]
    profileId: UUID
    usedAt: datetime
    params: 
        price: int
"""


async def get_coupons(user: discord.User) -> Dict:
    token: str = get_jwt_token(user)
    headers: Dict = {"Authorization": f"Bearer {token}"}
    response = requests.get(COUPON_URL, headers=headers)
    success = await handle_status_code(response)
    if success:
        return response.json()
    return HttpStatusCode.SERVER_PROBLEM


async def connect_coupon_by_promo_code(
    user: discord.User,
    promo_code: str
) -> CouponAddMessage:
    token: str = get_jwt_token(user)
    headers: Dict = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        COUPON_ADD_URL,
        json={"code": promo_code},
        headers=headers
    )
    success = await handle_status_code(response)
    if success:
        return CouponAddMessage.SUCCESS
    try:
        data = response.json()
        message = data.get("message", "Server problem")
    except requests.exceptions.JSONDecodeError:
        message = "Server problem"
    return CouponAddMessage.by_value(message)
