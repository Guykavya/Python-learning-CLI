from collections.abc import Iterable
from typing import Protocol


class Closeable(Protocol):
    def close(self) -> None: ...


def close_all(items: Iterable[Closeable]) -> int:
    count = 0
    for item in items:
        item.close()
        count += 1
    return count


def close_quietly(item: Closeable) -> bool:
    try:
        item.close()
    except Exception:
        return False
    return True
