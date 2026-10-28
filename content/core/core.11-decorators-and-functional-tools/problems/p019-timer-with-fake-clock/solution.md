## Approach

The factory receives `clock` and the inner functions close over it, so the same code runs with the real
clock or a fake one. The `finally` block records the duration in both cases (normal return or error)
without catching the error. The list lives on the wrapper, so each decorated function has its own.
`report` only reads that list.

## Code

```python
import time
from functools import wraps


def timed(clock=time.perf_counter):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                wrapper.durations.append(clock() - start)
        wrapper.durations = []
        return wrapper
    return decorate


def report(func):
    name = func.__name__
    times = func.durations
    if not times:
        return f"{name}: no calls"
    return f"{name}: {len(times)} calls, total {sum(times):.3f}s, slowest {max(times):.3f}s"
```

## Complexity

O(1) extra per call; `report` is O(n) for n recorded calls.

## Another way

Instead of storing durations on the wrapper, let the factory take a list too: `timed(records, clock=...)`.
Both are fine. The key idea is the same: anything that changes on its own (time, randomness, the network)
should be passed in, so a test can replace it with something fixed. Never test timing with `time.sleep`.
