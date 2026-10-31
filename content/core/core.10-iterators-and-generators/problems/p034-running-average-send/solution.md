## Approach

The generator's local variables survive between calls, so `total` and `count` live there. The
single line `received = yield average` does two jobs: it hands out the average, then it waits for
the next value. The first `next(g)` runs up to that line and hands out `None`, which is why priming
returns `None`.

## Code

```python
from collections.abc import Generator


def averager() -> Generator[float | None, float | None, None]:
    total = 0.0
    count = 0
    average = None
    while True:
        received = yield average
        if received is None:
            total = 0.0
            count = 0
            average = None
        else:
            total += received
            count += 1
            average = total / count
```

The type hint `Generator[Y, S, R]` means: it yields `Y`, receives `S` with `send`, and returns `R`.

## Complexity

O(1) time and O(1) memory per `send`. Nothing is stored except two numbers.

## Another way

A closure can do the same thing: an outer function with `total` and `count`, and an inner `add(x)`
that uses `nonlocal`. The generator version needs no `nonlocal` and keeps the "where am I" state for
free, which matters more when the protocol has several steps.
