## Approach

"Passed step k" means "passed steps 1..k". A session whose flags are not nested has a logging problem: we count it only as far as the chain holds and report how many there are, so the data owner can fix the logging.

## Code

```python
import numpy as np
import pandas as pd


def funnel_table(df, steps):
    flags = df[steps].astype(bool)
    passed = flags.cummin(axis=1)
    n = len(df)
    rows = [("sessions", n, np.nan, 100.0)]
    prev = n
    for s in steps:
        k = int(passed[s].sum())
        rows.append((s, k, k / prev * 100 if prev else np.nan, k / n * 100))
        prev = k
    t = pd.DataFrame(rows, columns=["step", "sessions", "% of previous step", "% of all sessions"])
    t["dropped"] = t["sessions"].shift(1) - t["sessions"]
    return t, int((flags & ~passed).any(axis=1).sum())
```

## Complexity

O(n x steps).

## Another way

Fix the logging first and keep this function as a **check**: if `n_inconsistent` is not 0, the report says so instead of hiding it.
