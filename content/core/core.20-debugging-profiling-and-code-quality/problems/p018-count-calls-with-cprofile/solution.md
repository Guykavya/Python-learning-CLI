## Approach

1. Make a new profiler, switch it on, run `fn(*args, **kwargs)`, switch it off in a `finally`
   block so it is off even when `fn` raises (the exception keeps travelling to the caller).
2. `pstats.Stats(profiler).stats` maps `(filename, line, name)` to
   `(primitive_calls, total_calls, tottime, cumtime, callers)`.
3. Skip built-ins (filename `"~"`) and add `total_calls` to a dictionary keyed by name.

`total_calls` vs `primitive_calls`: for `fib(10)` only one call is "primitive" (not made while
another `fib` was already running). The other 176 are recursive. A printed profile shows this as
`177/1` in the `ncalls` column.

## Code

```python
import cProfile
import pstats


def call_counts(fn, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        fn(*args, **kwargs)
    finally:
        profiler.disable()
    counts = {}
    for (filename, _line, name), (_primitive, total, *_rest) in pstats.Stats(profiler).stats.items():
        if filename == "~":
            continue
        counts[name] = counts.get(name, 0) + total
    return counts
```

## Complexity

The profiler adds a constant cost to every call (often 2x to 3x slower overall for code with
many small calls). Building the dictionary is O(number of distinct functions).

## Another way

`profiler.runcall(fn, *args, **kwargs)` does enable, call and disable (with the `finally`) in one
step:

```python
profiler = cProfile.Profile()
profiler.runcall(fn, *args, **kwargs)
```

A `collections.Counter` can replace the `counts.get(name, 0) + total` line:
`counts[name] += total`.
