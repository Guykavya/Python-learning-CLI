def to_int(value: int | str | None) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        return int(value)
    return value


def describe(value: int | str | list[int]) -> str:
    if isinstance(value, int):
        return f"int {value}"
    if isinstance(value, str):
        return f"str {value!r}"
    return f"list of {len(value)}"


def total_length(items: list[str | list[str]]) -> int:
    total = 0
    for item in items:
        if isinstance(item, str):
            total += len(item)
        else:
            total += sum(len(s) for s in item)
    return total


def first_text(values: list[int | str]) -> str | None:
    for v in values:
        if isinstance(v, str):
            return v
    return None
