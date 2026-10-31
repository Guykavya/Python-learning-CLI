import re

PHONE_RE = re.compile(r"(?:\+1[ -]?)?(?P<area>\([2-9]\d{2}\)|[2-9]\d{2})[-. ]?(?P<exchange>\d{3})[-. ]?(?P<line>\d{4})(?:\s*(?:ext\.?|x)\s*(?P<ext>\d{1,5}))?")


def parse_phone(s: str) -> dict | None:
    return None
