def safe_int(text: str) -> int | None:
    try:
        return int(text.strip())
    except ValueError:
        return None


def safe_int_or(text: str, default: int) -> int:
    n = safe_int(text)
    if n is None:
        return default
    return n


def parse_all(texts: list[str]) -> list[int]:
    return [n for n in map(safe_int, texts) if n is not None]
