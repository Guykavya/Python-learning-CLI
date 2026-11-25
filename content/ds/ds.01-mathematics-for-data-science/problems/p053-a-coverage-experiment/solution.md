## Approach

Coverage is a property of the *procedure*, so repeat the whole procedure and count how often it captures the truth.

## Code

```python
import numpy as np


def coverage(ci_fn, n, reps, seed=0):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(reps):
        lo, hi = ci_fn(rng.normal(size=n))
        hits += lo <= 0.0 <= hi
    return hits / reps
```

## Complexity

O(reps n).

## Another way

Plot coverage against `n`: the z-interval approaches 95% only slowly, the t-interval is right from the start.
