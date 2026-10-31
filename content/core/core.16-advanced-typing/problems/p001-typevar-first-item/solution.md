## Approach

A `TypeVar` is a placeholder for "some type, the same one everywhere in this signature". Writing `items: Sequence[T]` and `-> T` says: whatever the items are, that is what you get back. The checker fills `T` in at each call: `first([1, 2])` has `T = int`, `first("ab")` has `T = str`. Reading the hint `-> object` or `-> Any` would give no such promise.

`first_or` uses `T` three times (items, default, result), so the default must have the same type as the items. `last_or_none` returns `T | None`; the caller has to deal with the `None` before using the value.

## Code

```python
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
```

## Complexity

O(1) time and space for all three.

## Another way

On Python 3.12+ you can drop the `TypeVar` line and write `def first[T](items: Sequence[T]) -> T:`. The meaning is identical. Also `first_or` can be written as `return items[0] if items else default`; `len(items) == 0` is used above only to make the "empty" test explicit.
