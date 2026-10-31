# Quadratic to linear

A profile of a nightly job shows one function using 95% of the time:

```python
def common_items(a, b):
    result = []
    for x in a:
        if x in b and x not in result:
            result.append(x)
    return result
```

It is correct. It is also **quadratic**: `x in b` walks through the list `b` comparing items one
by one, and so does `x not in result`. For two lists of 100,000 items that is billions of
comparisons.

Rewrite `common_items(a, b)` in `solution.py` (the starter is the slow version above) so it does
an amount of work **proportional to `len(a) + len(b)`**, with exactly the same results:

- the items of `a` that also appear in `b`,
- in the order they first appear in `a`,
- each item only once,
- the inputs are not changed. All items are hashable.

**How it is graded.** The tests do not use a stopwatch. They pass in items that **count their
own comparisons** (`__eq__` calls). The quadratic version needs about `len(a) * len(b)`
comparisons, a linear one needs a small multiple of `len(a) + len(b)`. That count is the same on
every machine, so the test is never flaky.

**Example**

```python
common_items([3, 1, 3, 2, 5], [5, 3, 3, 9])
# [3, 5]
common_items(["a", "b"], [])
# []
```
