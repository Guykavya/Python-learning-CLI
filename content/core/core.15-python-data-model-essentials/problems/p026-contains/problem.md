# Membership tests with __contains__

`x in obj` calls `obj.__contains__(x)`. If that method is missing, Python falls back to iterating over
`obj`; if the object cannot be iterated either, you get `TypeError: argument of type ... is not iterable`.
Defining `__contains__` lets an object answer `in` without storing every value.

Write two classes in `solution.py`:

1. `Interval(lo, hi)`: `x in Interval(1, 10)` is `True` when `lo <= x <= hi` (both ends included). It
   stores only two numbers. Non-numbers (`"a"`, `None`) are simply `False` (not an error). Treat `int` and
   `float` as numbers.
2. `WordSet(words)`: `w in WordSet(["Hello", "World"])` ignores case (`"hello" in ...` is `True`). Items that
   are not strings are `False`.

**Example**

```python
print(5 in Interval(1, 10))      # True
print(10.5 in Interval(1, 10))   # False
print("a" in Interval(1, 10))    # False
ws = WordSet(["Hello", "World"])
print("hello" in ws, "x" in ws, 3 in ws)   # True False False
```
