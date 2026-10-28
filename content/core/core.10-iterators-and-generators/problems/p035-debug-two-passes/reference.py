from collections.abc import Iterable


def stats(numbers: Iterable[float]) -> tuple[int, float, float | None]:
    count = 0
    total = 0
    largest = None
    for x in numbers:
        count += 1
        total += x
        if largest is None or x > largest:
            largest = x
    return count, total, largest


def shares(numbers: Iterable[float]) -> list[float]:
    data = list(numbers)
    total = sum(data)
    if total == 0:
        raise ValueError("shares() needs numbers whose total is not zero")
    return [x / total for x in data]
