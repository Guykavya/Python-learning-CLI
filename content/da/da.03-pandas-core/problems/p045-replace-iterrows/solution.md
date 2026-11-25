## Approach

Replace the `if / elif / else` by `np.select`: a list of conditions (each a boolean column), a list of values, and a default. Conditions are checked in order and the first match wins, so `qty >= 10` must come before `qty >= 5`. Then the whole calculation is column arithmetic. Wrap the result in a Series with the input's index and the name `total`, as the loop did.

## Code

```python
import numpy as np
import pandas as pd


def line_totals(df):
    rate = np.select([df["qty"] >= 10, df["qty"] >= 5], [0.10, 0.05], default=0.0)
    return pd.Series(df["qty"] * df["unit_price"] * (1 - rate), index=df.index, name="total")
```

## Complexity

O(n) in compiled loops: three comparisons, one select and two multiplications over arrays. The `iterrows` loop is also O(n), but with a Python object per row, which is hundreds of times slower.

## Another way

`pd.cut(df["qty"], [0, 5, 10, np.inf], right=False, labels=[0.0, 0.05, 0.10]).astype(float)` gives the rate from the edges (left-closed bins: `[5, 10)` is 5%), and `df["qty"].map(...)` works when the quantity takes few values. `np.select` is the one that reads like the original `if / elif`.
