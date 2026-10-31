from collections import deque
from collections.abc import Iterable
from pathlib import Path


def last_n(items: Iterable[str], n: int) -> list[str]:
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return list(deque(items, maxlen=n))


def tail(path: str | Path, n: int = 10) -> list[str]:
    with open(path, encoding="utf-8") as f:
        lines = last_n(f, n)
    return [line.rstrip("\n") for line in lines]
