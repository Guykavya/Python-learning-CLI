## Approach

Name the differences once, then apply each formula. Naming intermediate values avoids long,
error-prone one-liners.

## Code

```python
import math

x1 = float(input())
y1 = float(input())
x2 = float(input())
y2 = float(input())
dx = x2 - x1
dy = y2 - y1
print(f"Straight line: {math.hypot(dx, dy):.3f}")
print(f"City blocks: {abs(dx) + abs(dy):.3f}")
```

## Why `math.hypot`

`hypot(dx, dy)` computes `sqrt(dx*dx + dy*dy)` but is written to avoid overflow and to lose less
precision for very large or very small values.

## Another way

`math.dist((x1, y1), (x2, y2))` takes two points directly. It uses tuples, which you will
study in core.05.
