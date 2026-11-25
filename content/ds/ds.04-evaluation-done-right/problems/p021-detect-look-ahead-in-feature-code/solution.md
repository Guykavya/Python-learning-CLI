## Approach

If deleting everything after `t` changes the value at `t`, the value depended on the future. This is a property test: it does not read the code, it checks its behaviour.

## Code

```python
import numpy as np


def uses_future(feature_fn, series, t):
    full = feature_fn(series).iloc[t]
    cut = feature_fn(series.iloc[: t + 1]).iloc[t]
    return bool(not np.isclose(full, cut, equal_nan=True))
```

## Complexity

Two feature computations.

## Another way

Run the check at many values of `t`, and on random series, inside your test suite. A single `t` can miss a leak that only shows near the end.
