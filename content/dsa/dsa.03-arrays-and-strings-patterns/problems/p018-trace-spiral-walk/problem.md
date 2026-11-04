# Trace the spiral boundaries

This program walks a 3 x 4 grid in spiral order. After each side it prints the values it took on that side and the
four boundaries `top bottom left right` **after** shrinking. Predict **exactly** what it prints. Do not run it.

```python
g = [[1, 2, 3, 4],
     [5, 6, 7, 8],
     [9, 10, 11, 12]]
top, bottom, left, right = 0, 2, 0, 3
out = []
print("start", top, bottom, left, right)
while top <= bottom and left <= right:
    side = [g[top][c] for c in range(left, right + 1)]
    out += side
    top += 1
    print("top", side, "->", top, bottom, left, right)
    side = [g[r][right] for r in range(top, bottom + 1)]
    out += side
    right -= 1
    print("right", side, "->", top, bottom, left, right)
    if top <= bottom:
        side = [g[bottom][c] for c in range(right, left - 1, -1)]
        out += side
        bottom -= 1
        print("bottom", side, "->", top, bottom, left, right)
    if left <= right:
        side = [g[r][left] for r in range(bottom, top - 1, -1)]
        out += side
        left += 1
        print("left", side, "->", top, bottom, left, right)
print(out)
```

Write your answer in `answer.txt`, one line per printed line. Lines look like `top [1, 2, 3, 4] -> 1 2 0 3`.
An empty side prints as `[]`.

## How to work

Draw the grid with row numbers 0..2 down the side and column numbers 0..3 across the top. Keep the four boundaries
in a small box and cross out each cell as it is taken. Before every side, read its `range(...)` with the **current**
boundaries; a `range` whose start is past its end gives nothing.

## After you answer

1. Count the values in the last line. Is every cell there exactly once?
2. In the second lap, why is the right side empty, and why is the bottom side not printed at all?
3. What would go wrong without the `if top <= bottom:` check? Which values would be taken twice?
