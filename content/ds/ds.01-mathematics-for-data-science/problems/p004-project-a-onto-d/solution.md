## Approach

The coefficient `a.d / d.d` says how many copies of `d` fit into the shadow; multiply `d` by it.

## Code

```python
import numpy as np


def project(a, d):
    a = np.asarray(a, dtype=float)
    d = np.asarray(d, dtype=float)
    dd = float(d @ d)
    if dd == 0:
        raise ValueError("cannot project onto the zero vector")
    return (float(a @ d) / dd) * d
```

## Complexity

O(n) time.

## Another way

Normalise `d` to a unit vector `u` first; then the projection is `(a . u) * u`.
