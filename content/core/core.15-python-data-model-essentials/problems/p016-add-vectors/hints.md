## Hint 1

What does Python call for `v + w`? Which object is `self` and which is `other`? Does the result have to be a new object or can you change `self`?

## Hint 2

Return `Vector(self.x + other.x, self.y + other.y)`. First check `isinstance(other, Vector)`; if it is not, `return NotImplemented` so Python raises the `TypeError` for you.

## Hint 3

```
def __add__(self, other):
    if other is not a Vector: return NotImplemented
    return Vector(self.x + other.x, self.y + other.y)
def __sub__(self, other): same with -
```
