# New, retained, resurrected, churned

Chapter section 8.1. Monthly active users (MAU) is one number made of four kinds of users. Splitting it explains *why* it moves.
A user is **active in month `m`** if they have a `login` in that calendar month. Only **complete months** count (before
`2025-07-01`).

| State of a user in month `m` | Definition |
|---|---|
| `new` | active in `m`, and `m` is the first month they were ever active |
| `retained` | active in `m` and also active in `m - 1` |
| `resurrected` | active in `m`, not active in `m - 1`, but active in an earlier month |
| `churned` | **not** active in `m`, but active in `m - 1` (a user is `churned` only in the **first** month of absence) |

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
    "signup_at": pd.to_datetime(["2025-01-02", "2025-01-03", "2025-02-02", "2025-03-04", "2025-01-05"]),
    "channel": "ads", "country": "IN"})
logins = {1: [1, 2, 3, 4, 5], 2: [1, 3], 3: [2, 3], 4: [3], 5: [1, 2, 5]}      # months in which each user logs in
rows = [(u, pd.Timestamp(2025, m, 10, 9)) for u, ms in logins.items() for m in ms]
events = pd.DataFrame({
    "event_id": range(1, len(rows) + 1),
    "user_id": [r[0] for r in rows], "event_time": [r[1] for r in rows], "event_type": "login"})
```

Return **one row per user and month in which the user has a state**, with columns `user_id`, `month` (the first day of the
month, a date) and `state`. Active months give `new` / `retained` / `resurrected`; the month right after an active month in which the
user is absent gives `churned` (if that month is complete). Months of longer absence get no row. Put the SQL in `QUERY`.

## Example

User 2 logs in during months 1 and 3 (January and March): `(2, Jan, new)`, `(2, Feb, churned)`, `(2, Mar, resurrected)`, `(2, Apr, churned)`.
User 4 logs in only in March: `(4, Mar, new)`, `(4, Apr, churned)`.
Two identities must hold when you count the states of one month: `MAU(m) = new + retained + resurrected`, and
`MAU(m-1) = retained + churned` (month `m`).
