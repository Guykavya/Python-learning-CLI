# Fix the funnel that grows

Chapter sections 7.2 and 10.1, and da.06 on fan-out. A teammate wrote this funnel query and the report shows **more purchasers than
people who started checkout**: a funnel that grows. Find the bug in `starter.py` and fix it.

```sql
SELECT 1 AS step, 'view_course' AS name, count(*) FILTER (WHERE e.event_type = 'view_course') AS users
FROM events e LEFT JOIN orders o USING (user_id)
UNION ALL
SELECT 2, 'add_to_cart', count(*) FILTER (WHERE e.event_type = 'add_to_cart')
FROM events e LEFT JOIN orders o USING (user_id)
UNION ALL
SELECT 3, 'checkout_start', count(*) FILTER (WHERE e.event_type = 'checkout_start')
FROM events e LEFT JOIN orders o USING (user_id)
UNION ALL
SELECT 4, 'purchase', count(o.order_id)
FROM events e LEFT JOIN orders o USING (user_id)
```

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("users", users)
con.register("events", events)
con.register("orders", orders)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5],
    "signup_at": pd.to_datetime(["2025-03-01"] * 5),
    "channel": ["organic", "ads", "ads", "referral", "organic"],
    "country": ["IN", "IN", "US", "UK", "US"]})
events = pd.DataFrame({
    "event_id": list(range(1, 15)),
    "user_id": [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 1, 2],
    "event_time": pd.to_datetime(["2025-03-02 10:00", "2025-03-02 10:05", "2025-03-02 11:00", "2025-03-02 12:00", "2025-03-02 12:30",
                                  "2025-03-03 10:00", "2025-03-03 11:00", "2025-03-03 12:00", "2025-03-04 10:00", "2025-03-04 10:30",
                                  "2025-03-05 10:00", "2025-03-06 10:00", "2025-04-02 12:30", "2025-04-03 12:00"]),
    "event_type": ["view_course", "view_course", "add_to_cart", "checkout_start", "purchase", "view_course", "add_to_cart", "checkout_start",
                   "view_course", "add_to_cart", "view_course", "view_course", "purchase", "purchase"]})
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003],
    "user_id": [1, 1, 2],
    "order_time": pd.to_datetime(["2025-03-02 12:30", "2025-04-02 12:30", "2025-04-03 12:00"]),
    "plan": ["monthly", "monthly", "monthly"],
    "amount": [499, 499, 499]})
```

The fixed `QUERY` must return one row per step with the same columns as the broken one:

| column | meaning |
|---|---|
| `step` | 1 to 4 |
| `name` | `view_course`, `add_to_cart`, `checkout_start`, `purchase` |
| `users` | the number of **distinct users** who have an event of that type |

(This is the *unordered* funnel of Ch. 7.3: it counts users who did the step at all.) Each step must be at most the previous
one on the example data, and the counts must be **users**, not rows. Put the fixed SQL in `QUERY` in `solution.py`.

## Example

User 1 has two `view_course` events and two orders; joined to `orders`, each of their events appears twice. Counting rows gives
more than the number of users. The fix is to count distinct users, and to stop joining a table that the question does not need
(`events` already has the purchase events).
