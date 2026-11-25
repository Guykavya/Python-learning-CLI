# Seven days or seven rows?

Chapter section 9.4. A small kiosk only records days **with** sales, so its daily table has gaps. The owner wants,
for every recorded day, the revenue of the **last 7 calendar days** (that day and the 6 before it). `rolling(7)` looks
at the last 7 *rows*, which on a table with gaps can reach back weeks.

Write `rolling_week(daily)`:

- `daily` has the columns `date` (no time, one row per day with sales, **in any order**) and `revenue`;
- return a frame with the columns `date`, `revenue`, `week_total`: the same rows, sorted by date, fresh index, where
  `week_total` is the sum of `revenue` over the dates `date - 6 days` to `date`, both included;
- the first days have a shorter history; sum what there is (no `NaN`);
- do not change the input.

## Example

```python
import pandas as pd

daily = pd.DataFrame({"date": pd.to_datetime(["2025-03-12", "2025-03-01", "2025-03-04"]),
                      "revenue": [7.0, 10.0, 5.0]})
out = rolling_week(daily)
print(out["date"].dt.strftime("%m-%d").tolist(), out["week_total"].tolist())
```
```text
['03-01', '03-04', '03-12'] [10.0, 15.0, 7.0]
```

The window of 12 March is 6 to 12 March, so neither 1 nor 4 March is in it: 7.0. A 7-**row** window
(`rolling(7, min_periods=1)`) would add all three rows (22.0).
