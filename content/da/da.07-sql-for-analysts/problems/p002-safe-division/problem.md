# Safe division

Chapter section 2.2. In DuckDB, `1 / 0` does **not** raise an error: it returns `inf` (infinity), and `NULLIF(0, 0)` returns
`NULL`. An infinite rate in a report is a bug nobody notices until a chart breaks. When the denominator can be zero, divide by
`NULLIF(denominator, 0)`: the result is then `NULL`, which means "undefined".

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
    "country": ["IN", "IN", "US", "UK", "IN"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6],
    "user_id": [1, 1, 2, 3, 4, 5],
    "event_time": pd.to_datetime(["2025-01-03 10:00", "2025-01-04 09:00", "2025-01-10 12:00", "2025-02-02 08:00",
                                  "2025-02-14 09:00", "2025-03-05 11:00"]),
    "event_type": ["view_course", "purchase", "view_course", "view_course", "purchase", "login"]})
```

Return **one row per country**:

| column | meaning |
|---|---|
| `country` | the country |
| `viewers` | users of that country with at least one `view_course` event |
| `buyers` | users of that country with at least one `purchase` event (viewers or not) |
| `purchase_rate` | `buyers / viewers`, and `NULL` when the country has **no viewers** |

Every user must be counted once. Put the SQL in `QUERY`.

## Example

`IN` has viewers 1 and 2, and user 1 bought, so `viewers = 2`, `buyers = 1`, `purchase_rate = 0.5`.
`UK` has a single user who bought without ever viewing a course (a direct link): `viewers = 0`, `buyers = 1`, and the rate is
`NULL`, not `inf` and not 0.
