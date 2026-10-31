import re


def tokens(s: str) -> list[str]:
    return [part for part in re.split(r"[,;\s]+", s) if part]
