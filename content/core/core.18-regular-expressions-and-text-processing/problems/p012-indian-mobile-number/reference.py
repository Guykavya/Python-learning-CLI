import re

MOBILE_RE = re.compile(r"(?:\+91[ -]?|0)?[6-9][0-9]{4}[ -]?[0-9]{5}")


def is_mobile(s: str) -> bool:
    return MOBILE_RE.fullmatch(s.strip()) is not None
