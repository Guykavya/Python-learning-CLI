## Approach

The bug is the same in both functions: they read `numbers` more than once. A list can be read many
times, so Ravi's list tests pass. A generator is an iterator, and an iterator is used up after one
pass. In `stats`, `list(numbers)` reads everything, then `sum` sees nothing (0) and `max` of nothing
raises `ValueError`. In `shares`, `sum` reads everything and the list comprehension gets `[]`.

The two fixes are different on purpose:

- `stats` can be done in **one pass**, so do it in one loop with O(1) memory.
- `shares` needs the total before the first division, so it needs **two passes**. Store the items
  once in a list, then read the list twice. This uses O(n) memory, and that is the honest cost of
  this problem.

## Code

```python
from collections.abc import Iterable


def stats(numbers: Iterable[float]) -> tuple[int, float, float | None]:
    count = 0
    total = 0
    largest = None
    for x in numbers:
        count += 1
        total += x
        if largest is None or x > largest:
            largest = x
    return count, total, largest


def shares(numbers: Iterable[float]) -> list[float]:
    data = list(numbers)
    total = sum(data)
    if total == 0:
        raise ValueError("shares() needs numbers whose total is not zero")
    return [x / total for x in data]
```

## Complexity

`stats`: O(n) time, O(1) memory. `shares`: O(n) time, O(n) memory.

## Another way

For `stats` you could write `it = iter(numbers)` and take the first item with `next(it, None)` to
start `largest`. For `shares` there is no way around storing the items: `itertools.tee` would also
store them internally (see the tee problem), so a plain list is simpler and just as good.
A good habit: if a function needs two passes, call `list()` **once at the top** and say so in the
docstring.
