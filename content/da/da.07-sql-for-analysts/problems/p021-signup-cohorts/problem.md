# Signup cohorts

Chapter section 6.1. A **cohort** is a group of users who share a starting event; here, the **month of sign-up**. The first
number of any retention table is the size of each cohort: the denominator of every percentage after it. It must come from
`users`, not from `events`: a user who signed up and never did anything is still part of the cohort.

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
    "signup_at": pd.to_datetime(["2025-01-05 10:00", "2025-01-31 23:59", "2025-02-01 00:00", "2025-02-14 09:00",
                                 "2025-02-20 18:00", "2025-04-02 12:00"]),
    "channel": ["organic", "ads", "ads", "referral", "organic", "ads"],
    "country": ["IN", "IN", "US", "UK", "US", "IN"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3],
    "user_id": [1, 1, 3],
    "event_time": pd.to_datetime(["2025-01-05 10:00", "2025-02-02 09:00", "2025-02-01 00:00"]),
    "event_type": ["login", "login", "login"]})
```

Return one row per cohort month:

| column | meaning |
|---|---|
| `cohort` | the first day of the sign-up month, as a date |
| `cohort_size` | the number of users who signed up in that month |

Put the SQL in `QUERY`. Users 2, 4, 5 and 6 have no events at all (or none that matter): they still count. Row order does not matter.

## Example

User 2 signed up on 31 January at 23:59 and user 3 on 1 February at 00:00: one minute apart, but **different cohorts**
(`2025-01-01` and `2025-02-01`). The result has rows for January, February and April. March has no sign-ups and no row.
