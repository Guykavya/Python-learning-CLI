## Approach

The exact answer uses the complement; the simulation estimates the same number, which lets you check the formula.

## Code

```python
import numpy as np


def p_shared_birthday(k):
    if k > 365:
        return 1.0
    p_all_different = 1.0
    for i in range(k):
        p_all_different *= (365 - i) / 365
    return 1.0 - p_all_different


def simulate_birthday(k, trials, seed=0):
    rng = np.random.default_rng(seed)
    days = np.sort(rng.integers(0, 365, size=(trials, k)), axis=1)
    return float((np.diff(days, axis=1) == 0).any(axis=1).mean())
```

## Complexity

Exact: O(k). Simulation: O(trials k log k).

## Another way

For small probabilities `p ~ 1 - exp(-k (k - 1) / 730)` is a good approximation.
