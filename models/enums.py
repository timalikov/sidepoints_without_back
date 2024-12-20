from __future__ import annotations
import enum


class StatusCode(enum.Enum):
    SUCCESS = 0
    BAD = 1


class HttpStatusCode(enum.Enum):
    SUCCESS = 0
    SERVER_PROBLEM = 1


class PaymentStatusCode(enum.Enum):
    SUCCESS = 0
    NOT_ENOUGH_MONEY = 1
    SERVER_PROBLEM = 2
    OPBNB_PROBLEM = 3


class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNIMPORTANT = ""


class Languages(enum.Enum):
    RU = "Russian"
    EN = "English"
    ES = "Spanish"
    FR = "French"
    DE = "German"
    IT = "Italian"
    PT = "Portuguese"
    ZH = "Chinese"
    JA = "Japanese"
    KO = "Korean"
    AR = "Arabic"
    HI = "Hindi"
    TR = "Turkish"
    FA = "Persian"
    UNIMPORTANT = ""


class CouponType(enum.Enum):
    FREE_ORDER = "Free Order Coupon"
    ORDER_VALUE = "1$ Fixed Price Coupon"
    DISCOUNT_PERCENTAGE = "{percent}% Off Coupon"
    DISCOUNT = "$5 Off Coupon"

    @classmethod
    def by_string_name(cls, input_str) -> CouponType:
        for finger in cls:
            if finger.name == input_str:
                return finger
        raise ValueError(f"{cls.__name__} has no name matching {input_str}")
    
    @classmethod
    def get_value(cls, coupon: dict) -> str:
        coupon_type: CouponType = CouponType.by_string_name(coupon["type"])
        if coupon_type == cls.DISCOUNT_PERCENTAGE:
            try:
                percent = coupon["params"]["discount"]
            except KeyError:
                percent = 50
            return coupon_type.value.format(
                percent=percent
            )
        return coupon_type.value
    

class CouponAddMessage(enum.Enum):
    SUCCESS = "Success"
    HAS_OF_TYPE = "User already has coupon of this type"
    INVALID_PROMO_CODE = "No value present"
    SERVER_PROBLEM = "Server problem"

    @classmethod
    def by_value(cls, input_str) -> CouponType:
        for finger in cls:
            if finger.value == input_str:
                return finger
        return CouponAddMessage.SERVER_PROBLEM
