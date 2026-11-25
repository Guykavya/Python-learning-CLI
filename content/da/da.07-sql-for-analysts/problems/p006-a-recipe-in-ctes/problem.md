# A recipe in CTEs

Chapter section 3.1. A long question is easier to write as a **recipe**: one `WITH` step per idea, each with a name and a known
grain (what one row is). Here is a question that needs three steps.

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
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-01-25", "2025-02-14", "2025-03-05"]),
    "channel": ["organic", "ads", "organic", "ads", "referral"],
    "country": ["IN", "IN", "US", "UK", "US"]})
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005],
    "user_id": [1, 1, 2, 3, 4],
    "order_time": pd.to_datetime(["2025-01-10 09:00", "2025-02-12 10:00", "2025-01-20 18:30", "2025-02-03 07:45", "2025-02-25 12:00"]),
    "plan": ["monthly", "monthly", "annual", "monthly", "annual"],
    "amount": [499, 499, 3999, 499, 3999]})
```

*"For each acquisition channel and each month of the user's **first purchase**, how many buyers are there, and how much
revenue did those buyers bring in total (all their orders, renewals included)?"*

Write `QUERY` with **at least three CTEs**, one per step:

1. `first_purchase`: one row per user who ever bought, with the time of their first order;
2. `buyer_channel`: that table joined to `users` to get each buyer's channel (and the month of the first purchase, as a date);
3. `revenue`: the total of **all** orders of each buyer.

The final `SELECT` returns one row per `channel` and `first_purchase_month`:

| column | meaning |
|---|---|
| `channel` | the buyer's channel |
| `first_purchase_month` | first day of the month of the buyer's first order, as a date |
| `buyers` | number of buyers in the group |
| `revenue` | sum of all orders of those buyers |

The CTE names are yours to choose, but the query must contain at least three CTEs. Put the SQL in `QUERY`.

## Example

User 1 (organic) first bought on 10 Jan and renewed on 12 Feb (two orders, 998 in total). Their row lands in
`('organic', '2025-01-01')`, **not** in February: the month of the *first* purchase decides the group, while all the orders count in
`revenue`. User 5 never bought and does not appear.
