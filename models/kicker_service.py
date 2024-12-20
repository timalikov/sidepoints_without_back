from typing import Dict, Optional

from models.enums import CouponType


def build_service_price(service: Dict, coupon: Optional[Dict] = None) -> float:
    def _build_free_order(service_price: float, coupon: Dict) -> float:
        return 0
    
    def _build_discount(service_price: float, coupon: Dict) -> float:
        return max(service_price - 5, 0)
    
    def _build_discount_percentage(service_price: float, coupon: Dict) -> float:
        try:
            discount_percent = coupon["params"]["discount"]
        except:
            discount_percent = 50
        return service_price - (service_price * (discount_percent / 100))
    
    def _build_order_value(service_price: float, coupon: Dict) -> float:
        return 1

    service_price = float(service["service_price"])
    if not coupon:
        return service_price
    coupon_type: CouponType = CouponType.by_string_name(coupon["type"])
    return {
        CouponType.FREE_ORDER: _build_free_order,
        CouponType.DISCOUNT: _build_discount,
        CouponType.DISCOUNT_PERCENTAGE: _build_discount_percentage,
        CouponType.ORDER_VALUE: _build_order_value
    }[coupon_type](service_price, coupon)
