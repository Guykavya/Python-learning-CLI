from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasArea(Protocol):
    def area(self) -> float: ...


@runtime_checkable
class Named(Protocol):
    name: str


def total_area(things: Iterable[object]) -> float:
    total = 0.0
    for thing in things:
        if isinstance(thing, HasArea):
            total += thing.area()
    return total


def names_of(things: Iterable[object]) -> list[str]:
    names: list[str] = []
    for thing in things:
        if isinstance(thing, Named) and isinstance(thing.name, str):
            names.append(thing.name)
    return names


def classify(thing: object) -> str:
    has_area = isinstance(thing, HasArea)
    has_name = isinstance(thing, Named)
    if has_area and has_name:
        return "both"
    if has_area:
        return "area"
    if has_name:
        return "name"
    return "neither"
