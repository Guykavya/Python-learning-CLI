## Hint 1

A `@classmethod` receives the class it was **called on** as `cls`: for `Velocity.from_string(...)`,
`cls` is `Velocity`. Inside a normal method, which expression gives you the class of `self`? (It is
not `self.__class__.__name__`, which is only a string.)

## Hint 2

`"3;4".split(",")` gives `['3;4']`, one part. `"a,b"` gives two parts, but `float("a")` raises its
own `ValueError` with a different message. Catch it, and raise your own message `from` it.

## Hint 3

```text
parse_pair(text):            # @staticmethod
    parts = text.split(",")
    if len(parts) != 2: raise ValueError(message)
    try: return float(parts[0]), float(parts[1])
    except ValueError as err: raise ValueError(message) from err

from_string(cls, text):      # @classmethod
    x, y = cls.parse_pair(text); return cls(x, y)
zero(cls):                   # @classmethod
    return cls(0.0, 0.0)
scaled(self, k):  return type(self)(self.x * k, self.y * k)
plus(self, other): return type(self)(self.x + other.x, self.y + other.y)
```
