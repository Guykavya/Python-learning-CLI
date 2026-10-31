# Unary operators: -v, abs(v), bool(v)

Not every operator has two sides. `-v` calls `__neg__`, `+v` calls `__pos__`, `abs(v)` calls
`__abs__`, and `bool(v)` (also `if v:`) calls `__bool__`.

`Vector(x, y)` is started for you. Add:

- `-v`: a new Vector with both coordinates negated.
- `+v`: a new Vector equal to `v`.
- `abs(v)`: the length as a float, `sqrt(x*x + y*y)` (use `math.hypot` or `math.sqrt`).
- `bool(v)`: `False` only for the zero vector `Vector(0, 0)`.

**Example**

```python
v = Vector(3, 4)
print(-v)            # Vector(-3, -4)
print(abs(v))        # 5.0
print(bool(Vector(0, 0)), bool(v))   # False True
print([bool(x) for x in (Vector(0, 1), Vector(0, 0))])   # [True, False]
```
