# Month over month

Chapter section 5.3. Growth needs the previous period **next to** the current one: `lag(x) OVER (ORDER BY month)`. If a month
is missing from the table (no orders at all), `lag` jumps to an older month and the growth is computed against the wrong
period. Build the list of months first, with revenue 0 for empty months. Then a percentage change from a zero month is
**undefined** (`NULL`), not infinite.

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("orders", orders)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005],
    "user_id": [1, 2, 3, 1, 4],
    "order_time": pd.to_datetime(["2025-01-05 10:00", "2025-01-20 11:00", "2025-02-14 09:00", "2025-04-02 18:00", "2025-04-30 23:30"]),
    "plan": ["monthly", "annual", "monthly", "monthly", "annual"],
    "amount": [400, 600, 1500, 200, 400]})
```

Return one row for **every month from the first to the last order month** (including empty ones):

| column | meaning |
|---|---|
| `month` | first day of the month (a date) |
| `revenue` | total `amount` of the month, 0 for a month without orders |
| `prev_revenue` | revenue of the previous month, `NULL` for the first month |
| `change` | `revenue - prev_revenue`, `NULL` for the first month |
| `pct_change` | `change * 100 / prev_revenue` (so +25% is `25.0`), `NULL` for the first month **and** when `prev_revenue` is 0 |

Put the SQL in `QUERY`.

## Example

January 1000, February 1500 (`change` 500, `pct_change` 50.0), **March has no orders**: a row with `revenue = 0`, `change = -1500`,
`pct_change = -100.0`; April 600 has `prev_revenue = 0` (March, not February) and `pct_change = NULL`.
