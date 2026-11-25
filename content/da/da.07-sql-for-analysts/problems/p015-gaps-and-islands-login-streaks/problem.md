# Gaps and islands: login streaks

Chapter section 4.8. For sorted days, `day - row_number()` is **constant inside a run of consecutive days** and jumps when a day
is skipped. Group by that constant and every group is one run (an "island"). The trick needs **one row per user and day**:
two logins on the same day would break the numbering, so de-duplicate first.

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("events", events)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
events = pd.DataFrame({
    "event_id": list(range(1, 19)),
    "user_id": [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 1],
    "event_time": pd.to_datetime([
        "2025-01-01 09:00", "2025-01-02 08:00", "2025-01-02 21:00", "2025-01-03 10:00", "2025-01-05 11:00", "2025-01-06 12:00",
        "2025-01-06 18:00",
        "2025-01-01 07:00", "2025-01-03 07:00", "2025-01-05 07:00",
        "2025-01-10 10:00", "2025-01-11 10:00",
        "2024-12-30 23:00", "2024-12-31 01:00", "2025-01-01 02:00", "2025-01-02 03:00", "2025-01-02 04:00",
        "2025-01-04 10:00"]),
    "event_type": ["login"] * 17 + ["view_course"]})
```

Return, for each user who has at least one `login` event, the **longest streak of consecutive login days**:

| column | meaning |
|---|---|
| `user_id` | the user |
| `longest_streak` | the largest number of consecutive calendar days with at least one `login` |

Only `login` events count (a `view_course` on another day does not extend a streak). Several logins on a day count as one day.
A user with no login does not appear. Put the SQL in `QUERY`.

## Example

User 1 logged in on days 1, 2 (twice), 3, 5 and 6 January (and viewed a course on the 4th, which does not count): the runs are
`1-2-3` and `5-6`, so `longest_streak = 3`. User 4 logged in on 30 Dec, 31 Dec, 1 Jan and 2 Jan (two logins on the 2nd): one run
of 4 days, **across the new year**.
