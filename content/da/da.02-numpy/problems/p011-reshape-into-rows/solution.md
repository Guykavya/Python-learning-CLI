## Approach

`reshape(-1, k)` asks for `k` columns and lets NumPy compute the rows: `len(x) // k`. Reshaping a contiguous array is a view (Ch. 6.2), so no data moves. NumPy would raise its own `ValueError` for a bad `k`, but its message talks about shapes; checking first lets the message speak the caller's language ("10 values into rows of 4").

## Code

```python
import numpy as np


def to_rows(x, k):
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    if len(x) % k != 0:
        raise ValueError(f"cannot split {len(x)} values into rows of {k}")
    return x.reshape(-1, k)
```

## Complexity

O(1): a view only changes shape and strides.

## Another way

`x.reshape(len(x) // k, k)` gives the same result. If the logger may stop mid-minute, `x[: len(x) - len(x) % k].reshape(-1, k)` drops the incomplete last minute instead of failing; that is a choice the caller should make, which is why this function raises.
