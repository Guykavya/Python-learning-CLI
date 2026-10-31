from collections.abc import Iterable


def stats(numbers: Iterable[float]) -> tuple[int, float, float | None]:
    count = len(list(numbers))
    total = sum(numbers)
    largest = max(numbers) if count else None
    return count, total, largest


def shares(numbers: Iterable[float]) -> list[float]:
    total = sum(numbers)
    return [x / total for x in numbers]
