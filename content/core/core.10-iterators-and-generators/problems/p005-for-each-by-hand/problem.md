# for_each without a for loop

Write `for_each(iterable, action)` in `solution.py`. It calls `action(item)` for every item of `iterable`, in order,
and returns **how many items** it handled.

The point of this exercise: you may **not** use a `for` loop or a comprehension. Use `iter()`, `next()`,
and `StopIteration`, exactly like the hand-written loop in the chapter. The test checks your source code.

**Examples**

```python
seen = []
for_each([5, 6, 7], seen.append)   # returns 3, seen is [5, 6, 7]
for_each("ab", print)              # prints a, then b; returns 2
for_each([], print)                # returns 0
```

If you pass an iterator that is already partly used, `for_each` continues from where it is.
