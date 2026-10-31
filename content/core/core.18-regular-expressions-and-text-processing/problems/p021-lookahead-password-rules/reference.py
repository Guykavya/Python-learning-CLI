import re

STRONG_RE = re.compile(r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])\S{8,}")


def strong(pw: str) -> bool:
    return STRONG_RE.fullmatch(pw) is not None
