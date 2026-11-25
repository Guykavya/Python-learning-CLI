# `GROUP BY ALL` and `EXCLUDE`

Chapter section 2.3. Two DuckDB conveniences remove repeated typing (and a whole class of "column not in GROUP BY" mistakes):

- `GROUP BY ALL` groups by every selected column that is **not** an aggregate.
- `SELECT * EXCLUDE (col, ...)` means "all columns except these".

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

Return how many events each combination of **channel, country and event type** has:

| column | meaning |
|---|---|
| `channel`, `country` | from `users` |
| `event_type` | from `events` |
| `events` | number of events in that combination |

Your query **must use both features**: `SELECT * EXCLUDE (event_id) FROM events` somewhere (a CTE is a good place; `event_id` is
not needed for this question) and `GROUP BY ALL` for the final grouping. The test checks the result *and* that both are in
your SQL. Put the SQL in `QUERY`.

## Example

User 1 is `organic` in `IN` and has three events (`view_course`, `purchase`, `purchase`). Among other rows, the result holds
`('organic', 'IN', 'purchase', 2)` and `('organic', 'IN', 'view_course', 1)`.
