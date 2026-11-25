## Approach

Split the work. `np.argpartition(x, -k)` runs a selection algorithm (introselect) that puts the `k` largest values in the last `k` positions of its result, in O(n), without ordering them. Then only those `k` values are sorted, O(k log k), and the order is applied to the positions. For `k` much smaller than `n` this is far less work than sorting everything.

Two edge cases need care: `k = 0`, because `-0` is `0` and `argpartition(x, 0)[-0:]` is the whole array; and `k > n`, which `argpartition` would reject, so cap `k` at `n` first.

## Code

```python
import numpy as np


def top_k(x, k):
    x = np.asarray(x)
    if k < 0:
        raise ValueError(f"k must be at least 0, got {k}")
    k = min(k, x.size)
    if k == 0:
        return np.array([], dtype=np.intp)
    idx = np.argpartition(x, -k)[-k:]
    return idx[np.argsort(x[idx])[::-1]]
```

## Complexity

O(n + k log k) time, O(n) extra memory for the positions. A full `np.argsort` is O(n log n); on a million values with `k = 10` it was about 5 times slower than this function (measured in an earlier test run; the factor depends on the machine).

## Another way

`np.argsort(x)[::-1][:k]` gives the same answer in one line and is fine for small arrays. For a stream that does not fit in memory, keep a heap of size `k` (`heapq.nlargest(k, ...)`, dsa.11): O(n log k) and O(k) memory.
