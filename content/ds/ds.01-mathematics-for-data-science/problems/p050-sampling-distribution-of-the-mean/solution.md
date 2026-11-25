## Approach

Simulate the experiment of the theory: many samples, one mean each.

## Code

```python
import numpy as np


def sample_means(draw, n, reps, seed=0):
    rng = np.random.default_rng(seed)
    return np.asarray(draw(rng, (reps, n))).mean(axis=1)
```

## Complexity

O(reps n).

## Another way

Plot a histogram of the result for `n = 1, 4, 16, 64` to watch the bell shape appear.
