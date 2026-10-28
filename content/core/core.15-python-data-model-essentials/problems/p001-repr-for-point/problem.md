# Give Point a useful repr

Print a plain object and you get `<solution.Point object at 0x7f...>`. That tells you nothing.
The special method `__repr__` lets an object describe itself the way you would write it in code.

Write a class `Point` in `solution.py`:

- `Point(x, y)` stores `x` and `y`.
- `repr(p)` returns text that looks like the call that builds it: `Point(3, 4)`.
  Use the `repr` of the values, so `Point(1.5, -2)` shows as `Point(1.5, -2)` and
  `Point("a", "b")` shows as `Point('a', 'b')`.

**Example**

```python
p = Point(3, 4)
print(repr(p))      # Point(3, 4)
print(p)            # Point(3, 4)   (print falls back to __repr__ when there is no __str__)
print([p, Point(0, 0)])   # [Point(3, 4), Point(0, 0)]
```
