# Factories that respect subclasses

`starter.py` has a small `Vector` class with factory methods: `from_string("3,4")`, `zero()`, and
methods that return new vectors (`scaled`, `plus`). Every one of them hard-codes the class name:
`return Vector(...)`. That works for `Vector`, but look:

```python
>>> v = Velocity.from_string("3,4")
>>> v.kind()
'vector'           # we asked Velocity for an object and got a plain Vector!
>>> Velocity(1, 2).scaled(2).kind()
'vector'
```

Fix the class in `solution.py` so that every factory returns an object of the class it was called on.

### `Vector` (keep `__init__(self, x, y)` and `kind()`)

- `parse_pair(text)` stays a **staticmethod**: it only parses text and does not build objects.
  `"3,4"` -> `(3.0, 4.0)`. Spaces around the numbers are allowed (`" 3 , 4 "`). If there are not
  exactly two parts, or a part is not a number, raise `ValueError(f"expected 'x,y', got {text!r}")`
  (raise it from the original error with `from` when `float()` failed).
- `from_string(text)` becomes a **classmethod** that returns `cls(x, y)`.
- `zero()` becomes a **classmethod** that returns `cls(0.0, 0.0)`.
- `scaled(self, k)` and `plus(self, other)` return `type(self)(...)`, a new object of the **same
  class as `self`**. They never change `self`.

### Subclasses (keep them as in the starter)

- `Velocity(Vector)` with `unit = "m/s"` and `kind()` returning `"velocity"`.
- `Labeled(Vector)` with `__init__(self, x, y, label="?")`. Factories create it with the default label.

## Example

```python
type(Velocity.from_string("3,4")) is Velocity    # True
Velocity.zero().unit                             # 'm/s'
type(Velocity(1, 2).scaled(2)) is Velocity       # True
Labeled.from_string("1,2").label                 # '?'
Vector.parse_pair(" 3 , 4 ")                      # (3.0, 4.0)
Vector.from_string("3;4")                        # ValueError: expected 'x,y', got '3;4'
v = Vector(1, 2).plus(Vector(3, 4)); (v.x, v.y)  # (4, 6)
```
