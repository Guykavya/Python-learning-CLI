# The retention table

Chapter section 6.2. Retention asks: of the users who signed up in a month (the **cohort**), what share was **active** in month
0, 1, 2, ... after sign-up? Build it in steps with one grain per CTE: one row per user and cohort; one row per user and **active
month** (`DISTINCT`, so a user with 15 logins counts once); then one row per cohort and month number.

Definitions (copy them exactly):

- the cohort of a user is the month of `signup_at` (first day of that month);
- a user is **active in a month** if they have at least one `login` event in that month;
- only **complete months** count: ignore every event at or after `2025-07-01`;
- `month_number` = `date_diff('month', cohort, active_month)`: 0 is the sign-up month.

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
    "signup_at": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-01-25", "2025-02-02"]),
    "channel": ["organic", "ads", "ads", "referral"],
    "country": ["IN", "IN", "US", "UK"]})
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7],
    "user_id": [1, 1, 1, 2, 3, 3, 4],
    "event_time": pd.to_datetime(["2025-01-05", "2025-02-03", "2025-02-20", "2025-01-20", "2025-01-25", "2025-03-01", "2025-02-02"]),
    "event_type": "login"})
```

Return the **long form**: one row for each cohort and month number in which at least one user was active:

| column | meaning |
|---|---|
| `cohort` | first day of the sign-up month (a date) |
| `month_number` | months since sign-up (0, 1, 2, ...) |
| `active_users` | distinct users of the cohort active in that month |
| `cohort_size` | users in the cohort (all users, active or not) |
| `retention` | `active_users / cohort_size` (a number from 0 to 1) |

Put the SQL in `QUERY`. Row order does not matter.

## Example

The January cohort has users 1, 2, 3. In month 0 all three logged in (`retention = 1`); in February only user 1, who logged in
**twice** (counted once): `active_users = 1`, `retention = 1/3`; in March only user 3. The February cohort (user 4) has only
month 0: in later months nobody was active, so the long form has no row for them.
