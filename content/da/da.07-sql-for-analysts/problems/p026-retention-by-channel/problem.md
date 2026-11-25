# Retention by channel

Chapter section 6.7. Retention tables become decisions when split by a segment: does the acquisition channel matter? We use
**month-1 retention**: of the users who signed up in a month, the share with a `login` in the **next calendar month**.

Rules (state them in your report):

- Only users whose **month 1 is complete** are measured: cohort month + 1 month must be before `2025-07-01` (so cohorts January to
  May; June sign-ups are left out).
- "Active in month 1" means at least one `login` in the calendar month after the user's sign-up month.
- A channel with **fewer than 3 measured users** is too small to trust: its `m1_retention` is `NULL` (but its counts are shown).

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
    "user_id": list(range(1, 10)),
    "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03", "2025-03-15", "2025-02-10", "2025-04-02",
                                 "2025-05-30", "2025-03-03", "2025-06-10"]),
    "channel": ["ads", "ads", "ads", "ads", "organic", "organic", "organic", "referral", "ads"],
    "country": "IN"})
events = pd.DataFrame({
    "event_id": list(range(1, 11)),
    "user_id": [1, 2, 3, 3, 4, 5, 6, 8, 9, 9],
    "event_time": pd.to_datetime(["2025-02-02", "2025-01-25", "2025-03-04", "2025-02-03", "2025-05-01", "2025-03-10", "2025-05-03",
                                  "2025-04-02", "2025-07-02", "2025-06-10"]),
    "event_type": "login"})
```

Return one row per channel that has at least one measured user:

| column | meaning |
|---|---|
| `channel` | the channel |
| `users` | measured users (cohorts Jan-May) |
| `retained_m1` | measured users with a login in their month 1 |
| `m1_retention` | `retained_m1 / users`, or `NULL` when `users < 3` |

Put the SQL in `QUERY`.

## Example

`ads` has measured users 1, 2, 3, 4 (user 9 signed up in June: month 1 is July, not complete). User 1 (signup 5 Jan) logged in on 2 Feb:
retained. User 2 only logged in on 25 Jan (month 0): not retained. Users 3 and 4: user 3 has February and March logins
(signup 3 Feb: month 1 is March, retained); user 4 (signup 15 Mar) logged in on 1 May: month 2, not month 1.
`referral` has a single measured user: `users = 1`, `m1_retention = NULL`.
