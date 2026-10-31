# A timer as a context manager

A **context manager** is an object used in a `with` statement. Python calls `__enter__` when the
block starts (its return value goes after `as`) and `__exit__` when the block ends, **always**, even
when the block raises. Write `Timer` in `solution.py`:

- `Timer(clock=time.perf_counter)`: `clock` is any function that returns the current time as a
  number. (Tests pass a fake clock; do not call `time.perf_counter` directly.)
- `__enter__` reads the clock, sets `running = True` and **returns the timer itself**.
- `__exit__` reads the clock, stores the elapsed time, sets `running = False`, and does **not**
  hide exceptions from the block.
- `elapsed` is a property. Before any run it is `0.0`. While the block is running it is the time
  since `__enter__` (read the clock again). After the block it is the stored, frozen value.
- A timer can be used again: a new `with` replaces the stored value.

**Example**

```python
with Timer() as t:
    total = sum(range(1_000_000))
print(f"took {t.elapsed:.4f} s")     # took 0.0123 s   (your number will differ)
t.running                            # False
```
