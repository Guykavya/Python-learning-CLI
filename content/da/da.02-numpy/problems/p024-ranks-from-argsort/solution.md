## Approach

`order = argsort(key)` lists the positions from rank 0 upwards; the rank of position `order[r]` is `r`, so `result[order] = arange(n)` inverts the mapping (Ch. 15.6 does the same with a second `argsort`). Two details make ties go by position: `kind="stable"` keeps equal keys in their original order, and for descending we sort `-x` ascending instead of reversing an ascending result (reversing would put the later of two equal values first).

## Code

```python
import numpy as np


def ranks(x, descending=False):
    x = np.asarray(x)
    key = -x if descending else x
    order = np.argsort(key, kind="stable")
    result = np.empty(len(x), dtype=np.intp)
    result[order] = np.arange(len(x))
    return result
```

## Complexity

O(n log n) for the sort; the inversion is O(n).

## Another way

`np.argsort(key, kind="stable").argsort()` (argsort twice, Ch. 15.6) gives the same ranks; the second sort costs O(n log n) where the assignment costs O(n). Negating does not work for unsigned integers (`-np.uint8(3)` wraps round): convert them to a signed type first. For statistics you usually want *average* ranks for ties (pandas `rank`, da.03).
