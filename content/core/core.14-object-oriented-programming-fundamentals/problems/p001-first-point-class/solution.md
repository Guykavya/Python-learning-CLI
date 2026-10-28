## Approach

A class is a blueprint; each `Point(...)` call builds one object from it (chapter section 2).
Python then calls `__init__` with the new object as `self` (section 4), and `self.x = x` stores the
number **on that object**. Every method gets the object it was called on as `self` (section 3):
`a.distance_to(b)` runs `Point.distance_to(a, b)`.

`moved` must not change `self`. It builds and returns a fresh `Point`. This style, where an
operation gives back a new object instead of changing the old one, makes points safe to share.

## Code

```python
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def moved(self, dx, dy):
        return Point(self.x + dx, self.y + dy)
```

## Complexity

Every method is O(1): a few arithmetic steps, no loops.

## Another way

`math.hypot(dx, dy)` computes `sqrt(dx*dx + dy*dy)` in one call, and `math.dist((x1, y1), (x2, y2))`
works on two tuples. Later (section 6) you will see why `moved` could return `type(self)(...)` so a
subclass of `Point` gets a subclass object back.
