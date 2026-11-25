## Approach

Take the last full season and repeat it as often as needed.

## Code

```python
import numpy as np


def seasonal_naive(train, horizon, season=7):
    t = np.asarray(train, dtype=float)
    if len(t) < season:
        raise ValueError("need at least one full season of history")
    last = t[-season:]
    return np.array([last[i % season] for i in range(horizon)])
```

## Complexity

O(horizon).

## Another way

`np.tile(last, horizon // season + 1)[:horizon]`.
