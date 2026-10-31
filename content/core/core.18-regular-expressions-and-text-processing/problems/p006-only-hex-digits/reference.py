import re


def only_hex(s: str) -> bool:
    return re.fullmatch(r"[0-9a-fA-F]+", s) is not None
