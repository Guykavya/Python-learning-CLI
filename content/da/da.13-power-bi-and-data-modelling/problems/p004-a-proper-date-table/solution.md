## Approach

A calendar is generated, never loaded from the facts: if you built it from the fact dates, a day without sales would be missing and the chart of daily revenue would skip it.

## Code

```python
import pandas as pd


def date_table(start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if end < start:
        raise ValueError("end is before start")
    d = pd.date_range(start.normalize(), end.normalize(), freq="D")
    return pd.DataFrame({"DateKey": d.strftime("%Y%m%d").astype(int), "Date": d, "Year": d.year,
                         "Quarter": "Q" + d.quarter.astype(str), "MonthNum": d.month,
                         "MonthName": d.strftime("%b"), "YearMonth": d.strftime("%Y-%m")})
```

## Complexity

O(days).

## Another way

In Power BI, `CALENDAR(MIN(Sales[Date]), MAX(Sales[Date]))` or `CALENDARAUTO()` builds a date table in DAX; generating it in Python keeps it testable and identical in every tool.
