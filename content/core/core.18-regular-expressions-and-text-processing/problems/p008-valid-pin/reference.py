import re


def valid_pin(s: str) -> bool:
    return re.fullmatch(r"[0-9]{4,6}", s) is not None
