## Approach

A namedtuple is a tuple whose positions have names. Printing it shows the field names, and
`_replace` makes a changed copy because the tuple itself cannot change.

## Code

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
n = int(input())
points = []
for _ in range(n):
    x, y = [int(v) for v in input().split()]
    points.append(Point(x, y))
best = points[0]
for p in points:
    if p.x * p.x + p.y * p.y > best.x * best.x + best.y * best.y:
        best = p
print("Points:", len(points))
print("Farthest:", best)
print("Moved:", best._replace(x=best.x + 1))
print("Sum of x:", sum(p.x for p in points))
```

## Complexity

O(n) for reading and one pass to find the farthest point.

## Another way

With core.06 you could write `max(points, key=lambda p: p.x * p.x + p.y * p.y)`, which also
returns the first of equal points.
