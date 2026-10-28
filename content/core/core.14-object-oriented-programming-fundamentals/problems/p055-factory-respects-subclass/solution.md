## Approach

Hard-coding the class name inside a factory freezes the result type. Chapter section 6 shows the fix:

- **Alternative constructors** are `@classmethod`s that end with `return cls(...)`. Python passes the
  class the method was called on, so `Velocity.from_string` builds a `Velocity`.
- **Methods that return a new object of "my kind"** use `type(self)(...)`, the class of the object
  the method runs on.
- **Helpers that build nothing** (`parse_pair`) can stay `@staticmethod`: they do not need `cls`.

## Code

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def parse_pair(text):
        parts = text.split(",")
        if len(parts) != 2:
            raise ValueError(f"expected 'x,y', got {text!r}")
        try:
            return float(parts[0]), float(parts[1])
        except ValueError as err:
            raise ValueError(f"expected 'x,y', got {text!r}") from err

    @classmethod
    def from_string(cls, text):
        x, y = cls.parse_pair(text)
        return cls(x, y)

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0)

    def scaled(self, k):
        return type(self)(self.x * k, self.y * k)

    def plus(self, other):
        return type(self)(self.x + other.x, self.y + other.y)

    def kind(self):
        return "vector"


class Velocity(Vector):
    unit = "m/s"

    def kind(self):
        return "velocity"


class Labeled(Vector):
    def __init__(self, x, y, label="?"):
        super().__init__(x, y)
        self.label = label
```

`cls.parse_pair(text)` instead of `Vector.parse_pair(text)` also lets a subclass override the parsing.

## Complexity

O(n) for a text of length n; everything else is O(1).

## Another way

Some designs do **not** want `type(self)`: `plus` of a `Velocity` and a `Vector` could also be
defined to return a plain `Vector`. Decide on purpose. The general rule: if a subclass changes the
`__init__` signature in an incompatible way (for example, a required extra argument), `cls(x, y)`
breaks, and that subclass must override the factories. `Labeled` avoids this by giving `label` a
default.
