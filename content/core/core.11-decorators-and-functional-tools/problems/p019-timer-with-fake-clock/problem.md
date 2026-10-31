# @timed(clock=...): a testable timer

A timer decorator that calls `time.perf_counter()` directly is hard to test: real times change on every
run. The fix is to **inject** the clock: the decorator takes the clock function as an argument. The program
uses the real clock; a test passes a fake one that returns fixed numbers.

Write in `solution.py`:

1. `timed(clock=time.perf_counter)`: a decorator factory.
   - The wrapper reads `clock()` once before calling the function and once after, and appends
     `end - start` to the list `wrapper.durations` (empty right after decoration).
   - It records the duration **even if the function raises**; the error still reaches the caller.
   - It returns the function's result and keeps its metadata with `functools.wraps`.
2. `report(func)`: takes a function decorated with `@timed(...)` and returns one line:
   - no calls yet: `f"{name}: no calls"`
   - otherwise: `f"{name}: {count} calls, total {total:.3f}s, slowest {slowest:.3f}s"`

**Example with a fake clock**

```python
ticks = iter([10.0, 10.25, 20.0, 20.5])

def fake_clock():
    return next(ticks)

@timed(clock=fake_clock)
def work(x):
    return x * 2

work(1)            # 2    (clock gives 10.0 then 10.25: duration 0.25)
work(2)            # 4    (20.0 then 20.5: duration 0.5)
work.durations     # [0.25, 0.5]
report(work)       # 'work: 2 calls, total 0.750s, slowest 0.500s'
```

Note: `@timed()` with empty brackets uses the real clock.
