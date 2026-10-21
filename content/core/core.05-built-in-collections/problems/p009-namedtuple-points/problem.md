# Points with names

Create a namedtuple type `Point` with fields `x` and `y`:

```python
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
```

Read `n` (at least 1), then `n` lines of `x y` integers. Print:

```
Points: <n>
Farthest: <the point farthest from (0, 0)>
Moved: <that point with x increased by 1>
Sum of x: <sum of all x values>
```

Points must print the way namedtuples print, like `Point(x=3, y=4)`. Distance from the origin
can be compared using `x * x + y * y` (no square root needed). If several points are equally
far, use the **first** one. Make the moved point with `_replace`.

**Example**

Input:
```
3
1 1
3 4
-4 3
```
Output:
```
Points: 3
Farthest: Point(x=3, y=4)
Moved: Point(x=4, y=4)
Sum of x: 0
```
