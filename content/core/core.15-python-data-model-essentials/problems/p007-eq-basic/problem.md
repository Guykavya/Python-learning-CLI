# Equal by value with __eq__

By default two objects are equal only if they are the **same object** (`==` works like `is`).
`Point(1, 2) == Point(1, 2)` is `False` for a plain class. Define `__eq__` to compare by value.

Write a class `Point` in `solution.py`:

- `Point(x, y)` stores `x` and `y`.
- `a == b` is `True` when both coordinates match.
- Comparing a `Point` with something that is not a `Point` must **not** crash and must be `False`.
  The right way: return `NotImplemented` from `__eq__` for foreign types (Python then tries the
  other side and finally answers `False`).
- `a != b` must work too (you do not write `__ne__`).

**Example**

```python
print(Point(1, 2) == Point(1, 2))   # True
print(Point(1, 2) == Point(2, 1))   # False
print(Point(1, 2) == (1, 2))        # False
print(Point(1, 2) != Point(3, 4))   # True
print(Point(1, 2) in [Point(0, 0), Point(1, 2)])  # True
```
