## Approach

Sort a copy, slice off `k` items at each end, average the rest. Writing the end of the slice as `len(s) - k` avoids the `-0` trap.

## Code

```python
import math

def trimmed_mean(values, proportion=0.1):
    if not values:
        raise ValueError("empty list")
    if proportion < 0 or proportion >= 0.5:
        raise ValueError("proportion must be at least 0 and below 0.5")
    s = sorted(values)
    k = math.floor(len(s) * proportion)
    kept = s[k:len(s) - k]
    return sum(kept) / len(kept)
```

## Complexity

O(n log n) for the sort.

## Another way

`scipy.stats.trim_mean` does the same. A "winsorised" mean replaces the cut values by the nearest kept value instead of dropping them.
