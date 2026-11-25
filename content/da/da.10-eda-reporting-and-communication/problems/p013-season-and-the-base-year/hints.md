## Hint 1

`series.shift(12)` shifts by **position**. Why is that wrong when a month is missing? A `PeriodIndex` can be moved by 12 months: `index + 12`.

## Hint 2

```text
last_year = series.copy()
last_year.index = last_year.index + 12        # 2023-03 is now labelled 2024-03
return series - last_year.reindex(series.index)
```
