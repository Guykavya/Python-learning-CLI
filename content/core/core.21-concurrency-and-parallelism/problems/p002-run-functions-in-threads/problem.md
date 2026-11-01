# Run a function in many threads

Write `run_in_threads(func, args_list)`.

- `args_list` is a list of **tuples**. Each tuple holds the positional arguments for one call
  of `func`.
- Start **one `threading.Thread` per tuple**. Start **all** of them first, then `join` all of
  them, so the calls overlap.
- Return a list with the return value of each call, **in the same order as `args_list`**
  (not in the order the threads happened to finish).

A `Thread` throws away the return value of its target, so you need somewhere to put each
result. A list with one slot per call, filled by index, is the simplest place.

**Example**

```python
import time

def slow_square(x, delay):
    time.sleep(delay)
    return x * x

start = time.perf_counter()
print(run_in_threads(slow_square, [(1, 0.3), (2, 0.1), (3, 0.2)]))
print(round(time.perf_counter() - start, 1))
```

```text
[1, 4, 9]
0.3
```

The second call finished first, but the results are still in input order. The whole run takes
about as long as the **slowest** call (0.3 s), not the sum (0.6 s). (Your times will differ a
little.)

`run_in_threads(f, [])` returns `[]`.
