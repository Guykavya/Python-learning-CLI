# countdown: your first generator

Write a **generator function** `countdown(n)` in `solution.py` that yields `n`, `n - 1`, ... down to `1`.
If `n` is `0` or negative it yields nothing.

It must use `yield`. It must not build a list first.

**Examples**

```python
list(countdown(3))   # [3, 2, 1]
list(countdown(0))   # []
g = countdown(2)
next(g)              # 2
next(g)              # 1
next(g)              # raises StopIteration
```
