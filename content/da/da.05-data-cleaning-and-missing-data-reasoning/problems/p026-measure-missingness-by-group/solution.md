## Approach

A Boolean column of "is missing" turns the question into counting: `sum` is the number of missing values and `size` the
number of rows in each group. Dividing gives the rate. The key is put back as a column, and a two-key sort gives the
required order (rate descending, ties by the key ascending). A group without missing values has `sum = 0`, so it
naturally gets rate `0.0`.

## Code

```python
import pandas as pd


def missing_profile(df, by, col):
    t = df.assign(_missing=df[col].isna()).groupby(by)["_missing"].agg(["size", "sum"])
    t.columns = ["rows", "missing"]
    t["rate"] = t["missing"] / t["rows"]
    t = t.reset_index().sort_values(["rate", by], ascending=[False, True]).reset_index(drop=True)
    t["rows"] = t["rows"].astype(int)
    t["missing"] = t["missing"].astype(int)
    return t
```

## Complexity

O(n) for the grouping plus O(g log g) for sorting g groups.

## Another way

`df[col].isna().groupby(df[by]).mean()` gives the rate in one line (the chapter's version), but not the counts.
Counts matter: a rate of 50 percent from 2 rows is weaker evidence than 50 percent from 2,000 rows.
