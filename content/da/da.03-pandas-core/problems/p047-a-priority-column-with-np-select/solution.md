## Approach

Translate the numbered rules, in order, into three boolean columns and three values, and give the fallback as `default`. `np.select` evaluates "first match wins" for every row at once. For two conditions on columns use `&` with brackets (`vip & (days > 0)`), because `and` does not work on columns. `np.select` returns an array, so wrap it in a Series with the same index and the name `priority`.

## Code

```python
import numpy as np
import pandas as pd


def priority(df):
    conditions = [
        df["overdue_days"] > 30,
        df["vip"] & (df["overdue_days"] > 0),
        df["amount"] >= 5000,
    ]
    values = ["urgent", "high", "medium"]
    return pd.Series(np.select(conditions, values, default="low"),
                     index=df.index, name="priority")
```

## Complexity

O(n x rules): each rule is one vectorised pass.

## Another way

Start from `"low"` and overwrite from the **last** rule to the first: `out = pd.Series("low", index=df.index); out[amount >= 5000] = "medium"; ...`. Then the order is reversed (the strongest rule is applied last). `np.select` is clearer because the order of the list is the order of the rules.
