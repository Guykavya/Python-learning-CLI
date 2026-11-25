## Approach

One list comprehension: draw, take the mean, repeat. All randomness comes from the `rng` argument, so the result is reproducible.

## Code

```python
import numpy as np


def sample_means(pop, n, reps, rng):
    pop = np.asarray(pop)
    return np.array([rng.choice(pop, n, replace=False).mean() for _ in range(reps)])
```

## Complexity

O(reps x n) at least. Drawing without replacement from a big array costs more than with replacement.

## Another way

`rng.permuted`/`rng.integers` can draw all indices at once for speed. For the course sizes the loop is clear and fast enough.
