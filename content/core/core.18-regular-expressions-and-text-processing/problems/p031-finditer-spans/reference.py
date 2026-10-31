import re


def find_all_spans(pattern: str, text: str) -> list[tuple[int, int]]:
    return [m.span() for m in re.finditer(pattern, text)]
