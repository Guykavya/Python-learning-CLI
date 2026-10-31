## Hint 1

Trace `sum([v1, v2])` by hand: what is the first addition? Who answers it?

## Hint 2

In `__radd__(self, other)`, `other` is the *left* operand. When `other == 0` return `self` (or a copy). For anything else return `NotImplemented`.

## Hint 3

```
def __radd__(self, other):
    if other == 0 (and it is a number):  return Vector(self.x, self.y)
    return NotImplemented
```
