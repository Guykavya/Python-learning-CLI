# take: the first n items, no more

Write `take(iterable, n)` in `solution.py`. It returns a **list** with the first `n` items of `iterable`. If
there are fewer than `n` items, it returns all of them.

Two rules that the tests check:

1. It must work on an **infinite** iterable. Never call `list()` on the whole input.
2. It must take **exactly** `n` items from an iterator and **not one more**: after `take(it, 2)` the next
   `next(it)` must give the third item.

**Examples**

```python
take([5, 6, 7, 8], 2)      # [5, 6]
take("abc", 10)            # ["a", "b", "c"]
it = iter([1, 2, 3, 4])
take(it, 2)                # [1, 2]
next(it)                   # 3
```
