## Approach

Model the waiting line as a `deque` of `(name, remaining)` pairs. Each step:

1. `popleft()` the front job.
2. Run `ran = min(quantum, remaining)` units and record `(name, ran)`.
3. If `remaining - ran > 0`, `append` the job (with its new remaining work) at the back.

Stop when the deque is empty. Zero-work jobs are filtered out while building the deque, so they
never produce a slice. Building a new deque also leaves the caller's list untouched.

`finish_order` does not simulate again: it replays the slices, subtracting from a dict of
remaining work. A job finishes on the slice that brings it to zero. (Two jobs with the same
name would share one dict entry here; the tests for `finish_order` use distinct names.)

## Code

```python
from collections import deque


def round_robin(jobs: list[tuple[str, int]], quantum: int) -> list[tuple[str, int]]:
    if quantum < 1:
        raise ValueError(f"quantum must be at least 1, got {quantum}")
    queue = deque((name, work) for name, work in jobs if work > 0)
    slices = []
    while queue:
        name, left = queue.popleft()
        ran = min(quantum, left)
        slices.append((name, ran))
        if left - ran > 0:
            queue.append((name, left - ran))
    return slices


def finish_order(jobs: list[tuple[str, int]], quantum: int) -> list[str]:
    remaining = {}
    for name, work in jobs:
        remaining[name] = work
    order = []
    for name, ran in round_robin(jobs, quantum):
        remaining[name] -= ran
        if remaining[name] == 0:
            order.append(name)
    return order
```

## Complexity

The number of slices is S = sum of ceil(work / quantum). Each slice is O(1) with a deque, so
O(n + S) time and O(n + S) space for the result. With `list.pop(0)` each step would cost
O(n), making it O(n * S).

## Another way

`deque.rotate(-1)` moves the front item to the back in one call: keep `[name, left]` lists in the
deque, update `queue[0][1]` in place, and either `popleft()` the finished job or `rotate(-1)`.
Same complexity; the `popleft`/`append` version is easier to read.
