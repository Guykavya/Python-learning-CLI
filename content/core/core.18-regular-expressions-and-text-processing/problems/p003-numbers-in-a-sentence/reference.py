import re


def numbers(s: str) -> list[int]:
    return [int(text) for text in re.findall(r"-?[0-9]+", s)]
