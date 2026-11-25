## Approach

Coverage is measured against the truth, which only a simulation knows. The median passes; the maximum fails because the bootstrap distribution of the maximum has a hard upper edge at the sample maximum.

## Code

```python
import numpy as np


def boot_coverage(draw, n, stat, truth, reps, boot_reps, seed=0):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(reps):
        x = np.asarray(draw(rng, n), dtype=float)
        boots = np.array([stat(x[rng.integers(0, n, n)]) for _ in range(boot_reps)])
        lo, hi = np.quantile(boots, [0.025, 0.975])
        hits += lo <= truth <= hi
    return hits / reps
```

## Complexity

O(reps boot_reps n).

## Another way

Use the **subsampling** or a parametric bootstrap for extremes, or a method built for them (extreme-value theory).
