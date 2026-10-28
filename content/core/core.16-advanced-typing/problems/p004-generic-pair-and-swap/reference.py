from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


@dataclass(frozen=True)
class Pair(Generic[A, B]):
    first: A
    second: B

    def swap(self) -> "Pair[B, A]":
        return Pair(self.second, self.first)

    def map_first(self, func: Callable[[A], C]) -> "Pair[C, B]":
        return Pair(func(self.first), self.second)

    def map_second(self, func: Callable[[B], C]) -> "Pair[A, C]":
        return Pair(self.first, func(self.second))


def swap_tuple(p: tuple[A, B]) -> tuple[B, A]:
    a, b = p
    return (b, a)
