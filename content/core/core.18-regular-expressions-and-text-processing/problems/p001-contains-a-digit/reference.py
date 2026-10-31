import re


def has_digit(s: str) -> bool:
    return re.search(r"\d", s) is not None
