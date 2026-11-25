## Approach

Take `df[col]` once and read the parts from its `.dt` accessor. `day_of_week` counts Monday as 0, so Saturday and Sunday are 5 and 6: `>= 5`. For `NaT` the numeric parts come out as `NaN` and the comparison gives `False`, which matches the stated rule with no special code. Work on `df.copy()` so the caller's frame is not changed.

## Code

```python
def add_date_parts(df, col):
    d = df[col]
    out = df.copy()
    out["year"] = d.dt.year
    out["month"] = d.dt.month
    out["quarter"] = d.dt.quarter
    out["weekday"] = d.dt.day_name()
    out["is_weekend"] = d.dt.day_of_week >= 5
    return out
```

## Complexity

O(n): each part is one vectorised pass.

## Another way

`df.assign(year=lambda d: d[col].dt.year, ...)` does the same in one chain without a copy statement. If the column might still be text, convert first with `pd.to_datetime(df[col], format=...)`; `.dt` only works on real datetimes.
