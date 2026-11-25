# Share of the total

Chapter section 4.6. A window function can run **over the result of a `GROUP BY`**: first aggregate, then compare each group
with the grand total (`sum(x) OVER ()`) or accumulate in a chosen order (`sum(x) OVER (ORDER BY ...)`).

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("users", users)
con.register("orders", orders)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
users = pd.DataFrame({
    "user_id": [1, 2, 3],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-02-02"]),
    "channel": ["organic", "ads", "ads"],
    "country": ["IN", "US", "IN"]})
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005],
    "user_id": [1, 1, 2, 3, 2],
    "order_time": pd.to_datetime(["2025-02-10", "2025-03-10", "2025-02-11", "2025-03-01", "2025-03-20"]),
    "plan": ["monthly", "monthly", "annual", "annual", "monthly"],
    "amount": [499, 499, 3999, 3999, 499]})
```

Return one row for each `plan` and `country` (the country comes from `users`), **sorted by revenue from largest to smallest**:

| column | meaning |
|---|---|
| `plan`, `country` | the group |
| `revenue` | sum of `amount` in the group |
| `share` | `revenue` divided by the revenue of **all** groups together |
| `cumulative_share` | the running sum of `share` down the sorted list |

Break ties in revenue by `plan` (A to Z), then `country` (A to Z), so the order is the same every time. The shares add up to 1
and the last `cumulative_share` is 1. Put the SQL in `QUERY`.

## Example

On the data above the groups are `(annual, IN)` 3999, `(annual, US)` 3999, `(monthly, IN)` 998 and `(monthly, US)` 499; the total
is 9495. The first row has `share = 3999 / 9495`, the second also (a tie, broken by country), and the last
`cumulative_share = 1`.
