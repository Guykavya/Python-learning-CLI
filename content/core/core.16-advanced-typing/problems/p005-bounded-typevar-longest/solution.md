## Approach

A bare `T` stands for any type, and the checker only lets you do with it what every object supports. `len(item)` is not one of those things. `TypeVar("S", bound=Sized)` restricts `S` to types that are a `Sized` (they have `__len__`). Inside the function the checker accepts `len(item)`; at each call it still infers the **exact** type: `longest(["a"])` returns a `str`, not a `Sized`. That is the difference between a bound and writing `-> Sized`: the bound keeps the precise type.

The input may be an iterator that can only be walked once, so the code takes the first item with `next(it)` and then loops over the rest. Comparing with strict `>` keeps the first item on ties. `longest_or_none` reuses `longest` and turns its `ValueError` into `None`.

## Code

```python
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
```

## Complexity

O(n) time, O(1) extra space (one pass).

## Another way

`max(items, key=len)` returns the first maximal item too, and raises `ValueError` on an empty input, so `longest` can be `return max(items, key=len)` (mypy accepts it with the bound). `max(items, key=len, default=None)` is the one-liner for `longest_or_none`. Python 3.12+: `def longest[S: Sized](items: Iterable[S]) -> S:`.
