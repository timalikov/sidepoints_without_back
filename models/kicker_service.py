from typing import Dict, Optional

from models.enums import CouponType


def build_service_price(service: Dict, coupon: Optional[Dict] = None) -> float:
    service_price = float(service["service_price"])
    if not coupon:
        return service_price
    coupon_type: CouponType = CouponType.by_string_name(coupon["type"])
    return {
        CouponType.FREE_ORDER: 0,
        CouponType.DISCOUNT: max(service_price - 5, 0),
        CouponType.DISCOUNT_PERCENTAGE: service_price / 2,
        CouponType.ORDER_VALUE: 1
    }[coupon_type]
