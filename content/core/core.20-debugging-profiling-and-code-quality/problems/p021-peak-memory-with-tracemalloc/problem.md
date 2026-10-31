# Peak memory with tracemalloc

`tracemalloc` records every memory block Python allocates while it is tracing.
`tracemalloc.get_traced_memory()` returns a pair `(current, peak)`: the bytes allocated right now
and the **largest** amount that was allocated at any moment since tracing started (or since the
last `tracemalloc.reset_peak()`).

The peak is what decides whether a program fits in memory: a function may give back almost
everything before it returns, but if it held 2 GB for a moment on the way, a 1 GB machine
cannot run it.

Write `peak_bytes(fn, *args, **kwargs) -> int` in `solution.py`. It runs `fn(*args, **kwargs)`
and returns how many bytes **above the level at the start** were in use at the peak during the
call.

- If tracing is **not** running yet, start it before the call and stop it afterwards.
- If tracing **is** already running (`tracemalloc.is_tracing()`), someone else is using it:
  leave it running afterwards. Use `reset_peak()` so their earlier peak does not count.
- Measure from `current` at the start: `peak - start_current`.
- Stop tracing that you started even if `fn` raises, and let the exception through.

**Example**

```python
def with_list(n):
    return sum([i * i for i in range(n)])     # builds the whole list first

def with_generator(n):
    return sum(i * i for i in range(n))       # one value at a time

peak_bytes(with_list, 100_000)
# about 4_000_000 (machine-specific: the list itself plus 100,000 int objects)
peak_bytes(with_generator, 100_000)
# a few hundred bytes (machine-specific)
```

The two functions return the same number, but one of them needs thousands of times more memory
to get there.
