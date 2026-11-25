# Delivery times

Chapter section 13.4. An orders table has `ordered` and `delivered` (datetimes; `delivered` is `NaT` while the parcel
is still on its way) and `promised_days` (a number). Write `delivery_report(df)` that returns a **new** DataFrame with
two more columns at the end:

- `days`: the time from `ordered` to `delivered` as a **float number of days** (12 hours is `0.5`). `NaN` when the order
  was not delivered yet.
- `late`: `True` when `days` is **greater than** `promised_days`, otherwise `False`. An undelivered order is **not** late.

The input frame is not changed. No loops.

## Example

```python
import pandas as pd

from solution import delivery_report

df = pd.DataFrame({
    "ordered": pd.to_datetime(["2025-03-01 09:00", "2025-03-01 09:00", "2025-03-02 00:00"]),
    "delivered": pd.to_datetime(["2025-03-03 21:00", "2025-03-04 09:00", None]),
    "promised_days": [3, 3, 2],
})
out = delivery_report(df)
print(out["days"].tolist())
print(out["late"].tolist())
```

```text
[2.5, 3.0, nan]
[False, False, False]
```
