# First time of each step

Chapter section 7.2. The standard way to build a funnel is to compute, **for each user, the first time** they did each step (or
`NULL` if never). That gives a table with one row per user, which is easy to count, compare and order. The funnel steps are
`view_course`, `add_to_cart`, `checkout_start` and `purchase`.

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("users", users)
con.register("events", events)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-02-02", "2025-02-14", "2025-03-05"]),
    "channel": ["organic", "ads", "ads", "referral", "organic"],
    "country": ["IN", "IN", "US", "UK", "US"]})
events = pd.DataFrame({
    "event_id": list(range(1, 14)),
    "user_id": [1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 4, 5, 2],
    "event_time": pd.to_datetime(["2025-01-03 10:00", "2025-01-04 09:00", "2025-01-04 09:30", "2025-01-04 10:00", "2025-01-04 10:05",
                                  "2025-01-05 08:00", "2025-01-10 12:00", "2025-01-10 12:30", "2025-02-02 08:00", "2025-02-03 08:00",
                                  "2025-02-14 09:00", "2025-03-05 11:00", "2025-01-12 12:00"]),
    "event_type": ["login", "view_course", "view_course", "add_to_cart", "checkout_start", "purchase",
                   "view_course", "add_to_cart", "view_course", "view_course", "purchase", "login", "view_course"]})
```

Return **one row per user of `users`** (so exactly as many rows as users), with:

| column | meaning |
|---|---|
| `user_id` | the user |
| `t_view`, `t_cart`, `t_checkout`, `t_purchase` | the **earliest** `event_time` of that step for that user, `NULL` if the user never did it |

Users without any funnel event (user 5 only logged in) must still appear, with four `NULL`s. Put the SQL in `QUERY`.

## Example

User 1 viewed a course twice on 4 January (09:00 and 09:30): `t_view = 2025-01-04 09:00:00`, the **first** of the two.
User 2 viewed and added to cart but never started checkout: `t_checkout` and `t_purchase` are `NULL`.
