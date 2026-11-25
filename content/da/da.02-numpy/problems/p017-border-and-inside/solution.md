## Approach

Split the border into four slices that do not overlap: each one starts one cell after the previous one ended. A negative step walks backwards: `a[-1, -2::-1]` is the bottom row from the second-to-last column down to column 0, and `a[-2:0:-1, 0]` is the left column from the second-to-last row up to (not including) row 0. With one row or one column the "bottom" and "left" pieces would walk the same cells again, so those two shapes are handled first. The interior is one 2-D slice.

## Code

```python
import numpy as np


def border_values(a):
    h, w = a.shape
    if h == 1:
        return a[0, :].copy()
    if w == 1:
        return a[:, 0].copy()
    top = a[0, :]
    right = a[1:, -1]
    bottom = a[-1, -2::-1]
    left = a[-2:0:-1, 0]
    return np.concatenate([top, right, bottom, left])


def interior(a):
    return a[1:-1, 1:-1]
```

## Complexity

O(h + w) for the border (one copy of the border cells); O(1) for the interior view.

## Another way

A mask: `m = np.ones(a.shape, bool); m[1:-1, 1:-1] = False; a[m]` gives the border cells, but in **row order** (`0, 1, 2, 3, 4, 7, 8, ...`), not clockwise. Masks are the right tool when the order does not matter (for example "mean of the border pixels").
