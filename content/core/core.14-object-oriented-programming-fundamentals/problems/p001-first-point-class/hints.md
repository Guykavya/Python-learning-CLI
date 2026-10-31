## Hint 1

Where do `x` and `y` get stored? `__init__` runs when you write `Point(3, 4)`, and its first
parameter `self` is the brand-new object. What line puts the number `3` *on* that object?

## Hint 2

Inside a method, `self` is the point you called the method on, and `other` is the second point.
So `other.x - self.x` is the change in x. `math.sqrt` (or `math.hypot(dx, dy)`) gives the length.

## Hint 3

```
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return square root of (dx*dx + dy*dy)

    def moved(self, dx, dy):
        return a NEW Point built from self.x + dx and self.y + dy
```
