## Hint 1

Subtracting two datetime columns gives a timedelta column (section 13.4). `.dt.days` throws away the fraction of a day. How can you turn a timedelta into a *float* number of days? (Dividing by a timedelta of one day gives a plain number.)

## Hint 2

```text
gap  = out["delivered"] - out["ordered"]            # NaT where not delivered
days = gap / pd.Timedelta(days=1)                   # float, NaN where NaT
late = days > out["promised_days"]                  # NaN > x is False -> not late
```
You need no special case for undelivered orders: comparisons with `NaN` are `False`.
