from collections.abc import Iterable, Sized
from typing import TypeVar

S = TypeVar("S", bound=Sized)


def longest(items: Iterable[S]) -> S:
    it = iter(items)
    try:
        best = next(it)
    except StopIteration:
        raise ValueError("longest() of empty iterable") from None
    for item in it:
        if len(item) > len(best):
            best = item
    return best


def shortest(items: Iterable[S]) -> S:
    it = iter(items)
    try:
        best = next(it)
    except StopIteration:
        raise ValueError("shortest() of empty iterable") from None
    for item in it:
        if len(item) < len(best):
            best = item
    return best


def longest_or_none(items: Iterable[S]) -> S | None:
    try:
        return longest(items)
    except ValueError:
        return None
