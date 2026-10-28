from collections.abc import Iterable
from typing import Protocol


class HasArea(Protocol):
    def area(self) -> float: ...


class Named(Protocol):
    name: str


def total_area(things):
    return 0.0


def names_of(things):
    return []


def classify(thing):
    return "neither"
