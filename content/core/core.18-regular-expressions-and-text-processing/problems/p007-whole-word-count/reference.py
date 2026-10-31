import re


def count_word(text: str, word: str) -> int:
    pattern = r"\b" + re.escape(word) + r"\b"
    return len(re.findall(pattern, text, re.IGNORECASE))
