## Approach

1. Remember whether tracing was already on.
2. If not, start it. Either way reset the peak, so only this call's peak counts.
3. Read `current` (the starting level), run `fn`, read `peak`.
4. In `finally`, stop tracing only if **you** started it.
5. Return `peak - start_current` (never negative).

## Code

```python
import tracemalloc


def peak_bytes(fn, *args, **kwargs):
    was_tracing = tracemalloc.is_tracing()
    if not was_tracing:
        tracemalloc.start()
    try:
        tracemalloc.reset_peak()
        start_current, _ = tracemalloc.get_traced_memory()
        fn(*args, **kwargs)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        if not was_tracing:
            tracemalloc.stop()
    return max(0, peak - start_current)
```

## Complexity

`tracemalloc` hooks every allocation, so `fn` runs noticeably slower (often 2x or more) and
uses extra memory for the bookkeeping. Measure memory and speed in separate runs.

## Another way

To see **where** the memory came from, take snapshots instead:

```python
tracemalloc.start()
before = tracemalloc.take_snapshot()
result = fn()
after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:5]:
    print(stat)
```

Each line shows a source line and how many bytes it allocated (and kept) between the snapshots.
Snapshots show memory still held at the end; the peak shows the worst moment in between.
