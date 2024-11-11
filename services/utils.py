def hide_half_string(text: str) -> str:
    half_len: int = int(len(text) / 2)
    return text[:-half_len] + ("#" * half_len)
