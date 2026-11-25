# A complete calendar

Chapter section 5.1. A table of events has rows only for the days that **had** events, so `GROUP BY day` can never show a zero.
The fix is a **calendar** (a date spine): one row for every day, to which you `LEFT JOIN` the facts. DuckDB can build it inside the
query: `generate_series(DATE '2025-06-01', DATE '2025-06-30', INTERVAL 1 DAY)`.

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("events", events)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7, 8],
    "user_id": [1, 2, 1, 3, 2, 1, 3, 2],
    "event_time": pd.to_datetime(["2025-05-31 22:00", "2025-06-01 08:00", "2025-06-01 21:00", "2025-06-03 09:00",
                                  "2025-06-03 09:30", "2025-06-04 12:00", "2025-06-29 07:00", "2025-07-01 00:00"]),
    "event_type": ["login", "login", "login", "login", "view_course", "view_course", "login", "login"]})
```

Return **one row for every day of June 2025** (1 to 30 June, exactly 30 rows):

| column | meaning |
|---|---|
| `day` | the date |
| `logins` | the number of `login` events on that day, `0` when there are none |

Only `login` events count. A day on which only other events happened (3 June has a `view_course`) still needs a row. Events
outside June (31 May, 1 July) must not appear. Put the SQL in `QUERY`.

## Example

On the data above, 1 June has two logins (users 2 and 1), 2 June has none (a row with `logins = 0`), 3 June has one login (the
`view_course` of the same day is not a login), and 30 June has none: the 1 July login is outside the calendar.
