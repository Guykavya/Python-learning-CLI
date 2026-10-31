# A running average you feed with send()

A generator can also **receive** values. `value = yield result` gives `result` to the caller and
then waits. When the caller does `g.send(x)`, the `yield` expression becomes `x` and the body runs
on to the next `yield`.

Write a generator function `averager()` in `solution.py` that keeps a running average.

Rules:

1. **Priming.** A new generator must be started with `next(g)`. This first `next` returns `None`.
2. `g.send(number)` adds the number and returns the average of all numbers since the last reset,
   as a `float`.
3. `g.send(None)` (and so also `next(g)`, which sends `None`) **resets** the average: it forgets all
   numbers and returns `None`.
4. The generator never ends by itself.

**Example**

```python
g = averager()
next(g)        # None   (priming)
g.send(10)     # 10.0
g.send(20)     # 15.0
g.send(30)     # 20.0
next(g)        # None   (reset)
g.send(4)      # 4.0
```

Two separate generators must not share data: `a = averager()` and `b = averager()` keep their own numbers.
