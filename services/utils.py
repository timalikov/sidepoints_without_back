from decimal import Decimal
from uuid import UUID


def hide_half_string(text: str) -> str:
    half_len: int = int(len(text) / 2)
    return text[:-half_len] + ("#" * half_len)


def _json_converter(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, UUID):
        return str(obj)
