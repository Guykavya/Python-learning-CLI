def first_or_none(items: list[int]) -> int | None:
    if not items:
        return None
    return items[0]


def first_or_default(items: list[int], default: int) -> int:
    first = first_or_none(items)
    if first is None:
        return default
    return first
