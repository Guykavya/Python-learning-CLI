def total(numbers: list[int]) -> int:
    result = 0
    for n in numbers:
        result += n
    return result


def longest(words: list[str]) -> str:
    return max(words, key=len)


def price_of(menu: dict[str, float], item: str) -> float:
    return menu[item]


def shout_all(words: list[str]) -> list[str]:
    return [w.upper() for w in words]


def centre(points: list[tuple[int, int]]) -> tuple[float, float]:
    xs = sum(x for x, y in points) / len(points)
    ys = sum(y for x, y in points) / len(points)
    return xs, ys


def by_length(words: list[str]) -> dict[int, list[str]]:
    groups: dict[int, list[str]] = {}
    for w in words:
        groups.setdefault(len(w), []).append(w)
    return groups
