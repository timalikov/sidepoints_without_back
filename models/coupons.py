from typing import Dict
import requests
import discord

from config import (
    COUPON_URL
)

from services.common_http import handle_status_code
from models.payment import get_jwt_token
from models.enums import HttpStatusCodes


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
    return HttpStatusCodes.SERVER_PROBLEM
