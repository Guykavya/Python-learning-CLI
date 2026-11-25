# Daily changes

Chapter section 16.4. A Series `s` holds one number per day (sales, for example) and is already in date order. Write
`daily_changes(s)` that returns a DataFrame with the same index and three columns, in this order:

| column | meaning |
|---|---|
| `diff` | today minus yesterday |
| `pct_change` | today's change as a fraction of yesterday (`0.2` means +20%) |
| `running_total` | the sum of all values up to and including today |

The first row has no yesterday, so `diff` and `pct_change` are missing there. If **yesterday was zero**, the percentage
change is infinite (or `0/0`): replace every infinite value by a missing value, so the column holds only real numbers
and gaps. The input is not changed.

## Example

```python
import pandas as pd

from solution import daily_changes

s = pd.Series([100.0, 120.0, 90.0, 0.0, 50.0, 50.0], index=pd.date_range("2025-03-01", periods=6))
out = daily_changes(s)
print(out.columns.tolist())
print(out["diff"].tolist())
print(out["pct_change"].tolist())
print(out["running_total"].tolist())
```

```text
['diff', 'pct_change', 'running_total']
[nan, 20.0, -30.0, -90.0, 50.0, 0.0]
[nan, 0.19999999999999996, -0.25, -1.0, nan, 0.0]
[100.0, 220.0, 310.0, 310.0, 360.0, 410.0]
```
