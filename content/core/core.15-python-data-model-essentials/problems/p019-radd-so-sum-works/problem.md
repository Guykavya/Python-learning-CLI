# __radd__ so sum() works

`sum(items)` does not start from the first item. It starts from the integer `0` and computes
`0 + item1`, then `(that) + item2`, and so on. So the very first step is `0 + Vector(...)`: `int` does
not know `Vector`, Python falls back to `Vector.__radd__(v, 0)`.

`Vector(x, y)` with `__eq__`, `__repr__` and `__add__` is started for you. Add `__radd__` so that:

- `sum([v1, v2, v3])` returns the vector total.
- `sum([v1])` returns a Vector equal to `v1`.
- `0 + v` is allowed and gives `v` (a Vector equal to it).
- Any other left operand (`5 + v`, `"a" + v`) still raises `TypeError`.

(`sum([])` is the integer `0`; that is expected.)

**Example**

```python
vs = [Vector(1, 2), Vector(3, 4), Vector(5, 6)]
print(sum(vs))                 # Vector(9, 12)
print(sum(vs, Vector(0, 0)))   # Vector(9, 12)   (explicit start value)
print(0 + Vector(1, 1))        # Vector(1, 1)
5 + Vector(1, 1)               # TypeError
```
