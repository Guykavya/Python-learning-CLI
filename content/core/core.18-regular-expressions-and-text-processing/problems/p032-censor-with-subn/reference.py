import re


def censor(text: str, words: list[str]) -> tuple[str, int]:
    if not words:
        return (text, 0)
    alternatives = "|".join(re.escape(w) for w in words)
    pattern = re.compile(rf"\b(?:{alternatives})\b", re.IGNORECASE)
    return pattern.subn(lambda m: "*" * len(m.group()), text)
