from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    return items[0]


def first_or(items: Sequence[T], default: T) -> T:
    if len(items) == 0:
        return default
    return items[0]


def last_or_none(items: Sequence[T]) -> T | None:
    if len(items) == 0:
        return None
    return items[-1]
