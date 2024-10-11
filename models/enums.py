import enum


class StatusCodes(enum.Enum):
    SUCCESS = 0
    BAD = 1


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