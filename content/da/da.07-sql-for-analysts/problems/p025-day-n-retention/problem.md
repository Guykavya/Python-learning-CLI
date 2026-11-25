# Day-N retention

Chapter section 6.6. Day-N retention measures from each user's **own sign-up date**: "of the users who signed up, what share
logged in **exactly N days** after their sign-up date?" (the classic "exact day" version). Two rules matter:

- days are **calendar dates**: sign-up on 15 June at 09:00, day 7 is 22 June (any time of that day);
- only **eligible** users are counted: a user whose day N is **after the extraction date `2025-07-15`** cannot have been observed, so
  they leave the numerator **and** the denominator. A user is eligible for day N when `signup date + N days <= 2025-07-15`.

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
    "signup_at": pd.to_datetime(["2025-06-15 09:00", "2025-06-16 20:00", "2025-03-01 10:00", "2025-03-10 11:00", "2025-07-10 08:00"]),
    "channel": ["organic", "ads", "ads", "referral", "organic"],
    "country": ["IN", "IN", "US", "UK", "US"]})
events = pd.DataFrame({
    "event_id": list(range(1, 13)),
    "user_id": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5],
    "event_time": pd.to_datetime(["2025-06-16 07:00", "2025-06-22 22:00", "2025-07-15 06:00", "2025-06-17 10:00", "2025-06-25 10:00", "2025-06-16 20:00",
                                  "2025-03-02 23:30", "2025-03-08 06:00", "2025-03-31 12:00", "2025-03-10 11:00", "2025-07-10 08:00", "2025-07-11 09:00"]),
    "event_type": "login"})
```

Return **one row for each N in 1, 7 and 30**:

| column | meaning |
|---|---|
| `day_n` | 1, 7 or 30 |
| `eligible_users` | users whose day N is on or before 2025-07-15 |
| `retained_users` | eligible users with a `login` on their day N (the date `signup date + N`) |
| `retention` | `retained_users / eligible_users`, `NULL` if there is no eligible user |

Put the SQL in `QUERY`.

## Example

User 1 signed up on 15 June: day 30 is exactly 15 July, so user 1 is eligible for all three N, and has a login on 16 June (day 1),
22 June (day 7) and 15 July (day 30). User 2 signed up on 16 June: day 30 would be 16 July, after the extraction: not eligible
for N = 30 (but eligible for 1 and 7).
