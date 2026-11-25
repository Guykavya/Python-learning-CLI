## Approach

Build the null distribution by relabelling, then see where the observed difference falls in it.

## Code

```python
import numpy as np


def permutation_test(a, b, reps=5000, seed=0):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    obs = a.mean() - b.mean()
    pooled = np.concatenate([a, b])
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(reps):
        rng.shuffle(pooled)
        diff = pooled[:len(a)].mean() - pooled[len(a):].mean()
        count += abs(diff) >= abs(obs) - 1e-12
    return float(obs), (count + 1) / (reps + 1)
```

## Complexity

O(reps (na + nb)).

## Another way

For small groups enumerate every split exactly (`itertools.combinations`) instead of sampling (problem 57).
