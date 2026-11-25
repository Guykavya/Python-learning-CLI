# Weekly and monthly totals

Chapter section 9.3. `daily` is a full calendar of daily revenue (columns `date` and `revenue`, one row per day, as in
the previous problem). The report needs the same numbers per week and per month.

Write `period_totals(daily, freq)`:

- `freq` is a pandas frequency alias, passed straight to pandas: `"W-MON"` means weeks that **end on a Monday**,
  `"ME"` means calendar months (labelled by the month's last day);
- return a frame with the columns `period` (the label pandas gives each bin: the week's Monday, or the month's last
  day) and `revenue` (the sum in that bin), in time order, fresh index;
- pandas 3 removed the old alias `"M"`: `period_totals(daily, "M")` must raise `ValueError`, as pandas does. Do not
  translate it;
- do not change the input.

## Example

```python
import pandas as pd

daily = pd.DataFrame({"date": pd.date_range("2025-01-29", "2025-02-03"), "revenue": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]})
for freq in ["ME", "W-MON"]:
    out = period_totals(daily, freq)
    print(out["period"].dt.strftime("%Y-%m-%d").tolist(), out["revenue"].tolist())
```
```text
['2025-01-31', '2025-02-28'] [6.0, 15.0]
['2025-02-03'] [21.0]
```

29 January 2025 is a Wednesday, so all six days fall in the week that ends on Monday 3 February.
