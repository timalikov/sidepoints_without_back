import enum


class StatusCodes(enum.Enum):
    SUCCESS = 0
    BAD = 1


class HttpStatusCodes(enum.Enum):
    SUCCESS = 0
    SERVER_PROBLEM = 1


class PaymentStatusCodes(enum.Enum):
    SUCCESS = 0
    NOT_ENOUGH_MONEY = 1
    SERVER_PROBLEM = 2
    OPBNB_PROBLEM = 3


class Genders(enum.Enum):
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
    DISCOUNT_PERCENTAGE = "50% Off Coupon"
    DISCOUNT = "$5 Off Coupon"

    @classmethod
    def by_string_name(cls, input_str) -> "CouponType":
        for finger in cls:
            if finger.name == input_str:
                return finger
        raise ValueError(f"{cls.__name__} has no value matching {input_str}")
