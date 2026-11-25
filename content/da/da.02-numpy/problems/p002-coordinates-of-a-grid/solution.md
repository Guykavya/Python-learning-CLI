## Approach

`np.meshgrid(xs_1d, ys_1d)` returns two arrays of shape `(len(ys_1d), len(xs_1d))`: the first holds the x of each cell, the second the y. With `np.arange(w)` and `np.arange(h)` that is exactly the column and row number. Return them in the order the task asks: `(ys, xs)`.

## Code

```python
import numpy as np


def grid_coordinates(h, w):
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    return ys, xs
```

## Complexity

O(h · w) time and memory: two full grids.

## Another way

NumPy also has `np.indices((h, w))`, which returns both grids stacked in one array of shape `(2, h, w)`; `ys, xs = np.indices((h, w))` unpacks them. With broadcasting (Ch. 11) you can avoid building full grids at all: `np.arange(h)[:, None]` (shape `(h, 1)`) and `np.arange(w)` (shape `(w,)`) combine into `(h, w)` the moment you use them in a formula, which saves memory for big images.
