## Approach

`mask(cond, other)` puts `other` where `cond` is True and keeps all other cells, so the shape never changes. The condition `discount > cap` is False for a missing value (any comparison with `NaN` is False), so missing discounts are left alone. `assign` returns a **new** frame with the column replaced, so the input is untouched. The pandas 3 form `df.assign(discount=pd.col("discount").mask(pd.col("discount") > cap, cap))` says the same without repeating `df`.

## Code

```python
import pandas as pd


def cap_discounts(df, cap):
    return df.assign(discount=df["discount"].mask(df["discount"] > cap, cap))
```

## Complexity

O(n) and one new column.

## Another way

`df["discount"].clip(upper=cap)` does exactly this in one call. `where` with the opposite condition also works, but `df["discount"].where(df["discount"] <= cap, cap)` would replace the missing values as well, because `NaN <= cap` is False. Use `where(df["discount"].isna() | (df["discount"] <= cap), cap)` to be safe.
