# The immature cell is NULL, not 0

Chapter section 6.4. The retention triangle has empty cells below the diagonal: the **June** cohort cannot have a month-3 value
yet, because month 3 has not happened. Those cells must be `NULL` ("not observed yet"). If a `LEFT JOIN` from a full grid plus
`COALESCE(..., 0)` turns them into 0 the table claims "all June users vanished after three months", and a chart shows a cliff
along the diagonal. **Zero means "observed and nobody"; `NULL` means "not observed yet".**

Use the definitions of the previous problem (cohort = month of sign-up; active = a `login` in the month; complete months only,
events at or after `2025-07-01` ignored). A cell (cohort `c`, month number `k`) is **observed** when the month `c + k` months is
complete, i.e. `c + k months < 2025-07-01`.

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
    "user_id": [1, 2, 3, 4],
    "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03", "2025-06-10"]),
    "channel": ["organic", "ads", "ads", "referral"],
    "country": ["IN", "IN", "US", "UK"]})
events = pd.DataFrame({
    "event_id": list(range(1, 11)),
    "user_id": [1, 1, 1, 2, 3, 3, 3, 4, 4, 1],
    "event_time": pd.to_datetime(["2025-01-05", "2025-02-03", "2025-06-20", "2025-01-20", "2025-02-03", "2025-02-20", "2025-04-01",
                                  "2025-06-10", "2025-07-03", "2025-07-08"]),
    "event_type": "login"})
```

Return a **grid**: one row for each cohort that exists in `users` and for each month number from **0 to 5** (so `cohorts x 6`
rows), with these columns:

| column | meaning |
|---|---|
| `cohort`, `month_number` | the cell |
| `active_users` | distinct active users, `0` if the cell is observed and nobody was active, **`NULL` if the cell is not observed** |
| `cohort_size` | users in the cohort (always filled in) |
| `retention` | `active_users / cohort_size`, `NULL` when `active_users` is `NULL` |

Put the SQL in `QUERY`.

## Example

The June cohort (user 4) has month 0 observed (`active_users = 1`) and months 1 to 5 **NULL**: July (month 1) is not complete, even
though user 4 has a login on 3 July. The January cohort has month 2 (March) observed with **0** active users: a real zero. The
February cohort's month 5 is July: `NULL`.
