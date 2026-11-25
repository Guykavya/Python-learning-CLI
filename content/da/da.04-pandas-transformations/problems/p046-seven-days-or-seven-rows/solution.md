## Approach

A time-based window names a **span**, not a count: `rolling("7D")` at a date takes every row whose date is after
`date - 7 days` and at most `date`, i.e. the 7 calendar days ending that day, however many rows that is. It needs
the dates as a sorted `DatetimeIndex`, so sort first and set the index. A time window's `min_periods` is 1 by default,
so the first days sum what they have instead of giving `NaN`.

Worked by hand on the test data (dates in March, revenue): 1st 10, 2nd 20, 4th 5, 8th 40, 9th 1, 15th 100, 16th 7.
The window of the 8th is the 2nd to the 8th: 20 + 5 + 40 = 65. `rolling(7, min_periods=1)` would also add the 1st
(75). The window of the 15th is the 9th to the 15th: 1 + 100 = 101, while seven rows would reach back to the 1st (176).

## Code

```python
import pandas as pd


def rolling_week(daily):
    d = daily.sort_values("date").reset_index(drop=True)
    week = d.set_index("date")["revenue"].rolling("7D").sum()
    return d.assign(week_total=week.to_numpy())
```

## Complexity

O(n log n) for the sort; the rolling sum is one pass with a moving window.

## Another way

Reindex to a full calendar first (missing days = 0, section 9.2), then `rolling(7, min_periods=1).sum()` is a correct
7-day sum, and finally keep only the original dates. It is longer, but it makes the zero days visible, which helps for
a chart.
