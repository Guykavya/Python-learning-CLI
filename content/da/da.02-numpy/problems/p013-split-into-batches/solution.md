## Approach

The batch starts are `range(0, len(x), size)`. A slice `x[start:start + size]` is a view (Ch. 6.2), and a slice that runs past the end simply stops there, which makes the short last batch for free. An empty `x` gives an empty range, so an empty list.

## Code

```python
import numpy as np


def batches(x, size):
    if size <= 0:
        raise ValueError(f"size must be positive, got {size}")
    return [x[start:start + size] for start in range(0, len(x), size)]
```

## Complexity

O(len(x) / size) small view objects; no element is copied.

## Another way

`np.array_split` makes **nearly equal** pieces (sizes differ by at most one), which is not the same as "fixed size, short last batch". `np.split(x, range(size, len(x), size))` cuts at the given positions and does give the same batches as views; for an empty `x` it returns one empty batch instead of `[]`, so check that case.
