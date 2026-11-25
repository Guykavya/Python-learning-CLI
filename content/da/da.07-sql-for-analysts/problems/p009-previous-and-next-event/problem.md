# Previous and next event

Chapter section 4.3. `lag(x) OVER (PARTITION BY g ORDER BY t)` brings the value of the **previous row of the same group** onto
the current row, so you can compute "time since the last one" without a self join. The first row of each group has no previous
row: `lag` returns `NULL`.

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("orders", orders)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005, 9006],
    "user_id": [1, 1, 2, 1, 2, 3],
    "order_time": pd.to_datetime(["2025-01-10 09:00", "2025-01-12 23:30", "2025-01-15 10:00",
                                  "2025-01-13 00:10", "2025-02-20 08:00", "2025-03-01 12:00"]),
    "plan": ["monthly", "monthly", "annual", "monthly", "monthly", "annual"],
    "amount": [499, 499, 3999, 499, 499, 3999]})
```

For every order, return:

| column | meaning |
|---|---|
| `user_id`, `order_id` | as in `orders` |
| `order_time` | as in `orders` |
| `prev_order_time` | the time of the same user's **previous** order (by `order_time`), `NULL` for the user's first order |
| `days_since_prev` | the number of **calendar days** between the two order dates, `NULL` for the first order |

"Calendar days" means the difference of the *dates*: an order at 23:30 and the next one at 00:10 the next day are 1 day apart,
although only 40 minutes passed. Row order does not matter. Put the SQL in `QUERY`.

## Example

User 1's orders in time order are 9001 (10 Jan 09:00), 9002 (12 Jan 23:30), 9004 (13 Jan 00:10). Order 9004 has
`prev_order_time = 2025-01-12 23:30:00` and `days_since_prev = 1`. Order 9001 has `NULL` in both columns.
