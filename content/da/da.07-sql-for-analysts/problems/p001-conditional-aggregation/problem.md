# Conditional aggregation

Chapter section 2.1. One query can count several things at once if each count has its own condition:
`count(*) FILTER (WHERE ...)` (DuckDB) or `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` (portable).

LearnLoop has a `users` table (one row per user) and an `events` table (one row per event). Here is a tiny copy you can
experiment with:

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("users", users)
con.register("events", events)
# from solution import QUERY
print(con.execute(QUERY).df())
```

with

```python
users = pd.DataFrame({
    "user_id": [1, 2, 3, 4, 5, 6],
    "signup_at": pd.to_datetime(["2025-01-03", "2025-01-10", "2025-02-02", "2025-02-14", "2025-03-05", "2025-03-09"]),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads"],
    "country": ["IN", "IN", "US", "UK", "US", "IN"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "user_id": [1, 1, 2, 3, 3, 4, 5, 1],
    "event_time": pd.to_datetime(["2025-01-03 10:00", "2025-01-04 09:00", "2025-01-10 12:00", "2025-02-02 08:00",
                                  "2025-02-03 08:00", "2025-02-14 09:00", "2025-03-05 11:00", "2025-03-01 10:00"]),
    "event_type": ["view_course", "purchase", "view_course", "view_course", "purchase", "purchase", "login", "purchase"]})
```

Return **one row per channel** with these columns, in this order:

| column | meaning |
|---|---|
| `channel` | the acquisition channel |
| `users` | number of users from that channel |
| `buyers` | number of those users with **at least one** `purchase` event |
| `purchase_rate` | `buyers` divided by `users` (a number from 0 to 1) |

A user who bought three times is still **one** buyer. Every user counts once in `users`, even a user with no events at all.
Row order does not matter. Put the SQL in `QUERY`.

## Example

On the data above, `ads` has 3 users (2, 3, 6); users 3 has a purchase, so `buyers` is 1 and `purchase_rate` is 1/3.
`organic` has users 1 and 5: user 1 bought (twice), user 5 only logged in, so `buyers = 1` and the rate is 0.5.
