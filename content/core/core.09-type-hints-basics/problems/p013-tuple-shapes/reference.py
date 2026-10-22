def min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)


def sorted_unique(numbers: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(set(numbers)))


def split_name(full: str) -> tuple[str, str]:
    parts = full.split(maxsplit=1)
    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def head_tail(numbers: tuple[int, ...]) -> tuple[int | None, tuple[int, ...]]:
    if not numbers:
        return None, ()
    return numbers[0], numbers[1:]
