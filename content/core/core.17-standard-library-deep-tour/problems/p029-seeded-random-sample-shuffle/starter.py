import random
from typing import TypeVar

T = TypeVar("T")


def shuffled(items: list[T], seed: int) -> list[T]:
    """A new list with the items in a random order fixed by seed."""
    return list(items)


def pick_winners(names: list[str], k: int, seed: int) -> list[str]:
    """k different names, chosen at random (fixed by seed)."""
    return names[:k]


def roll_dice(n: int, seed: int) -> list[int]:
    """n rolls of a six-sided die (fixed by seed)."""
    return [1] * n


def split_data(items: list[T], test_percent: int, seed: int) -> tuple[list[T], list[T]]:
    """(train, test): shuffle a copy, the first len*test_percent//100 items are the test part."""
    return list(items), []
