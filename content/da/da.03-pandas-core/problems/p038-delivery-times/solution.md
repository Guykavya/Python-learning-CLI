## Approach

`delivered - ordered` is a timedelta column with `NaT` for undelivered orders. Dividing it by `pd.Timedelta(days=1)` gives float days (and `NaN` for `NaT`). `days > promised_days` is strictly greater, and since a comparison with `NaN` is `False`, an undelivered order is automatically not late.

## Code

```python
import pandas as pd


def delivery_report(df):
    out = df.copy()
    out["days"] = (out["delivered"] - out["ordered"]) / pd.Timedelta(days=1)
    out["late"] = out["days"] > out["promised_days"]
    return out
```

## Complexity

O(n), three vectorised operations.

## Another way

`(delivered - ordered).dt.total_seconds() / 86400` gives the same float. Use `dt.days` only when you want whole days on purpose, and say so in the column name (`whole_days`).

For nullable columns (`Float64`) the comparison would give `<NA>` instead of `False`; then add `.fillna(False)` (chapter 19.5).
