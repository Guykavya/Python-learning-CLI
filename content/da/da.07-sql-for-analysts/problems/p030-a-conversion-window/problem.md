# A conversion window

Chapter section 7.6. "Of the users who viewed a course, how many **bought within 7 days of their first view**?" A windowed
conversion needs the same **eligibility** rule as day-N retention: only users observed for the whole window count, otherwise
recent viewers (who have not had 7 days yet) pull the rate down.

Rules:

- the window starts at the user's **first** `view_course` time `t_view`;
- a user **converted** if they have a `purchase` at a time `t` with `t_view <= t <= t_view + 7 days` (exactly 7 days later still
  counts; 7 days and a minute does not; a purchase **before** the first view does not count);
- a user is **eligible** if they have a view and `t_view + 7 days <= 2025-07-15 00:00:00` (the data end at the extraction).

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
    "user_id": list(range(1, 8)),
    "signup_at": pd.to_datetime(["2025-06-01"] * 7),
    "channel": ["ads", "ads", "organic", "organic", "ads", "referral", "organic"],
    "country": "IN"})
events = pd.DataFrame({
    "event_id": list(range(1, 11)),
    "user_id": [1, 1, 2, 2, 3, 4, 6, 6, 7, 7],
    "event_time": pd.to_datetime(["2025-06-01 10:00", "2025-06-08 10:00", "2025-06-01 10:00", "2025-06-09 10:00", "2025-06-02 09:00",
                                  "2025-07-10 12:00", "2025-06-01 08:00", "2025-06-05 10:00", "2025-06-03 10:00", "2025-06-04 10:00"]),
    "event_type": ["view_course", "purchase", "view_course", "purchase", "view_course", "view_course", "purchase", "view_course",
                   "view_course", "purchase"]})
```

Return a **single row**:

| column | meaning |
|---|---|
| `eligible_users` | users with a view whose 7-day window is fully observed |
| `converted_users` | eligible users who converted |
| `conversion_rate` | `converted_users / eligible_users`, `NULL` when nobody is eligible |

Put the SQL in `QUERY`.

## Example

User 1 viewed on 1 June at 10:00 and bought on 8 June at 10:00: **exactly** 7 days, converted. User 2 bought at 10:00 on 9 June (8 days):
not converted. User 4 viewed on 10 July: the window ends on 17 July, after the extraction, so user 4 is **not eligible**.
User 6 bought on 1 June but viewed only on 5 June: the purchase is before the view and does not count.
