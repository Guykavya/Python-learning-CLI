# Catch the return value of a generator

A generator may end with `return value`. A `for` loop and `list()` throw that value away. It is
only visible in one place: the `StopIteration` exception has an attribute `.value` that holds it.

```python
def g():
    yield 1
    return "done"

it = g()
next(it)               # 1
try:
    next(it)
except StopIteration as e:
    print(e.value)     # done
```

Write two functions in `solution.py`.

## 1. `counted(iterable)` (a generator)

Yield every item of `iterable` unchanged, and at the end **return** how many items there were.

## 2. `drain(iterator)`

Run any iterator to its end **by hand** with `next()`, and return a tuple `(items, result)`:
`items` is the list of yielded items, and `result` is the generator's return value. A plain
iterator such as `iter([1, 2])`, or a generator without `return`, gives `None` as the result.

**Examples**

```python
drain(counted("abc"))      # (["a", "b", "c"], 3)
drain(counted([]))         # ([], 0)
drain(iter([7, 8]))        # ([7, 8], None)


def report():
    n = yield from counted(["x", "y"])
    yield f"total {n}"
    return "ok"

drain(report())            # (["x", "y", "total 2"], "ok")
```

The last example shows why the return value matters: `yield from` gives it to the outer generator.
