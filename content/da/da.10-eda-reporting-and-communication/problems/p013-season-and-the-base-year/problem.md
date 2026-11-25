# Season and the base year

Chapter section 4.6. Many KPIs are seasonal: churn may always be higher in some months. Comparing a month with the **previous month** mixes the season into the change.
Comparing it with the **same month a year earlier** removes the season.

Write `yoy_change(series)`. `series` is a monthly KPI with a `PeriodIndex` (freq `M`). Return a Series with the same index where each value is
`this month - the same month one year earlier`.

- Match months by **label**, not by position: if a month is missing from the data, the month twelve months later has no comparison and gets `NaN`.
- The first year has no earlier year: `NaN`.
- Keep the name of the series.

## Example

`2024-03 = 5.1` and `2023-03 = 4.6` give `0.5` for 2024-03. If 2023-03 is missing, 2024-03 is `NaN`, even if 2023-02 exists.
