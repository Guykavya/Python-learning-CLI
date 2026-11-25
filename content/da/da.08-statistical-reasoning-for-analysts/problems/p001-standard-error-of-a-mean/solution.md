## Approach

The SE is the spread of the data divided by `sqrt(n)`. NumPy's `std` divides by n by default; a sample needs `ddof=1`.

## Code

```python
import numpy as np


def standard_error(x):
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        raise ValueError("one value has no spread")
    return float(x.std(ddof=1) / np.sqrt(len(x)))
```

## Complexity

O(n).

## Another way

`scipy.stats.sem(x)` gives the same number (it also uses `ddof=1`).
