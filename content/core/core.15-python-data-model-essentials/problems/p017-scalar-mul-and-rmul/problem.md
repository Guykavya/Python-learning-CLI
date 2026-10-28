# Scalar multiplication and __rmul__

`v * 3` calls `v.__mul__(3)`. But `3 * v` first asks `int.__mul__(3, v)`, which does not know
`Vector` and answers `NotImplemented`; then Python tries `v.__rmul__(3)` ("reflected" multiplication).
You need **both** for the operator to feel natural.

`Vector(x, y)` is started for you. Add:

- `v * k` and `k * v` for a number `k` (int or float): both scale each coordinate.
- `v / k`: each coordinate divided by `k` (true division). Division by zero raises `ZeroDivisionError` naturally.
- `v * w` for two Vectors is **not** defined here: it must raise `TypeError`.
- Non-numbers (`"a"`, lists) must raise `TypeError` as well. Treat `int` and `float` as numbers (`bool` is fine).

**Example**

```python
v = Vector(1, 2)
print(v * 3)     # Vector(3, 6)
print(3 * v)     # Vector(3, 6)
print(v * 0.5)   # Vector(0.5, 1.0)
print(v / 2)     # Vector(0.5, 1.0)
v * v            # TypeError
```
