## Hint 1

What does `==` do by default for two different objects with the same data? Which method do you define to change it, and what are its two parameters?

## Hint 2

Check the type first with `isinstance(other, Point)`. If it fails, `return NotImplemented` (not `False`, and not an error). Then compare the two coordinate pairs.

## Hint 3

```
def __eq__(self, other):
    if other is not a Point: return NotImplemented
    return (self.x, self.y) == (other.x, other.y)
```
