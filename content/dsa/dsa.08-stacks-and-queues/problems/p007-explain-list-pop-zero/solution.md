## Approach

Separate the two questions: **correct?** (yes, the order is FIFO) and **fast?** (no, because of the shifting). Then give the cost of one call, the cost of `n` calls, the better structure, and the reason it is better.

## Model answer

See `answer.md`.

## What to check

- You said clearly that the code works; the issue is only the cost.
- You named the mechanism: the items **shift** left to fill box 0.
- You gave both costs: `O(n)` per call and `O(n^2)` for `n` calls.
- You named `deque.popleft()` and said it is `O(1)`, with a reason (pointers to both ends, nothing moves).

## Another way

You can show it with a measurement instead of an argument:

```python
import time
from collections import deque

n = 100_000
a = list(range(n))
t = time.perf_counter()
while a:
    a.pop(0)
print("list.pop(0):", round(time.perf_counter() - t, 2), "s")

d = deque(range(n))
t = time.perf_counter()
while d:
    d.popleft()
print("deque.popleft():", round(time.perf_counter() - t, 2), "s")
```

The exact times depend on your machine; the list version is many times slower, and doubling `n` roughly quadruples its time (the sign of `O(n^2)`), while the deque time only doubles.
