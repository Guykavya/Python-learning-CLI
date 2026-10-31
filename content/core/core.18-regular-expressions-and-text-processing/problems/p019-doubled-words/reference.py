import re

DOUBLED_RE = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)


def doubled_words(text: str) -> list[str]:
    return [m.group(1) for m in DOUBLED_RE.finditer(text)]
