from collections.abc import Callable
from typing import TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

IntTransform = Callable[[int], int]
IntPredicate = Callable[[int], bool]


def count_matching(items: list[int], pred: IntPredicate) -> int:
    return sum(1 for item in items if pred(item))


def apply_all(x: int, steps: list[IntTransform]) -> int:
    for step in steps:
        x = step(x)
    return x


def compose_two(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]:
    def composed(x: A) -> C:
        return g(f(x))

    return composed
