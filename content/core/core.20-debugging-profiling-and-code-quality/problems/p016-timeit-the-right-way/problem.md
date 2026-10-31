# timeit the right way

`timeit` follows three rules that make a timing trustworthy:

1. Run the code **many times in one batch** (`number`) and divide, because one call of a fast
   function is shorter than the clock can measure well.
2. Repeat the whole batch several times (`repeat`).
3. Report the **minimum** batch, not the mean. Noise (other programs, the garbage collector, a
   cold cache) can only make a run **slower**, never faster, so the fastest batch is the one
   closest to the true cost of your code.

Write `best_time(fn, number, repeat, timer=time.perf_counter) -> float` in `solution.py`.

- Do `repeat` batches. For each batch: read the timer once, call `fn()` exactly `number` times,
  read the timer once more.
- The time **per call** for that batch is `(end - start) / number`.
- Return the smallest per-call time over all batches.
- `timer` is a function with no arguments that returns the current time in seconds. Read it
  **only** at the start and end of each batch (exactly `2 * repeat` times in total), so its own
  cost is not added to every call.
- If `number < 1` or `repeat < 1`, raise `ValueError`.

The `timer` parameter is there so tests can pass a **fake clock** and get exact, repeatable
answers. In real use you leave it at the default.

**Example**

```python
from itertools import count

ticks = iter([0.0, 2.0,   10.0, 11.0,   20.0, 23.0])   # 3 batches: 2.0 s, 1.0 s, 3.0 s
calls = []
best_time(lambda: calls.append(1), number=4, repeat=3, timer=lambda: next(ticks))
# 0.25   -> the fastest batch took 1.0 s for 4 calls
len(calls)
# 12     -> 3 batches of 4 calls
```

With the real clock:

```python
best_time(lambda: sorted(range(1000)), number=1000, repeat=5)
# about 1e-05 (machine-specific)
```
