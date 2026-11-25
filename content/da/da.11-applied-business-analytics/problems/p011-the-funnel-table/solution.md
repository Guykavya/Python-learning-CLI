## Approach

One pass over the steps with a running previous count; `shift(1)` gives the row above for the `dropped` column.

## Code

```python
import numpy as np
import pandas as pd


def funnel_table(df, steps):
    n = len(df)
    rows = [("sessions", n, np.nan, 100.0)]
    prev = n
    for s in steps:
        k = int(df[s].sum())
        rows.append((s, k, k / prev * 100 if prev else np.nan, k / n * 100))
        prev = k
    t = pd.DataFrame(rows, columns=["step", "sessions", "% of previous step", "% of all sessions"])
    t["dropped"] = t["sessions"].shift(1) - t["sessions"]
    return t
```

## Complexity

O(n x steps).

## Another way

`df[steps].cumprod(axis=1).sum()` counts sessions that passed **every** step up to each one, which is the safer definition when the flags may be inconsistent (problem 16).
