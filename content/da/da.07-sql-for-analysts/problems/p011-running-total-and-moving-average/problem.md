# Running total and 7-day average

Chapter sections 4.5 and 5.1. Orders exist only on days that had orders. A moving average over "the last 7 rows" is a
7-**day** average only if every day has a row, so first build a **complete calendar** with `generate_series`, join the daily
revenue to it, and turn missing days into 0.

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("orders", orders)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004],
    "user_id": [1, 2, 1, 3],
    "order_time": pd.to_datetime(["2025-06-01 09:00", "2025-06-01 17:30", "2025-06-03 08:15", "2025-06-06 20:00"]),
    "plan": ["monthly", "annual", "monthly", "annual"],
    "amount": [499, 3999, 499, 3999]})
```

Return one row for every calendar day from the **first** order date to the **last** order date (both included):

| column | meaning |
|---|---|
| `day` | the date |
| `revenue` | total `amount` of the orders of that day, `0` on days without orders |
| `running_total` | the sum of `revenue` from the first day up to this day |
| `avg_7` | the average of `revenue` over this day and up to the 6 days before it (fewer at the start: the average of the days that exist) |

Put the SQL in `QUERY`. The order of rows does not matter.

## Example

On the data above the calendar runs from 1 to 6 June. Revenue per day is `4498, 0, 499, 0, 0, 3999`; the running total is
`4498, 4498, 4997, 4997, 4997, 8996`. On 3 June `avg_7` is `4997 / 3` because only three days exist so far.
