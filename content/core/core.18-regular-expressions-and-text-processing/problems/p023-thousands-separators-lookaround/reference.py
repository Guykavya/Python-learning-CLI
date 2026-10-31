import re

WESTERN_RE = re.compile(r"(?<=\d)(?=(?:\d{3})+$)")
INDIAN_RE = re.compile(r"(?<=\d)(?=(?:\d\d)*\d{3}$)")


def commas(n: int) -> str:
    return WESTERN_RE.sub(",", str(n))


def commas_indian(n: int) -> str:
    return INDIAN_RE.sub(",", str(n))
