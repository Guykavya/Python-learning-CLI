import re


def span_info(pattern: str, text: str) -> tuple[str, int, int] | None:
    m = re.search(pattern, text)
    if m is None:
        return None
    return (m.group(0), m.start(), m.end())
