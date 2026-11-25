# The latest row per user

Chapter section 4.7. "The most recent record per user" is one of the most common SQL tasks: the current status, the last
login, the latest plan. The pattern is to number each user's rows from newest to oldest and keep number 1, or to use
`arg_max`. Real data has **ties**: two events with the same timestamp, so you need a tie-break.

```python
import duckdb, pandas as pd
con = duckdb.connect()
con.register("events", events)
# from solution import QUERY
print(con.execute(QUERY).df())
```

```python
events = pd.DataFrame({
    "event_id": [1, 2, 3, 4, 5, 6, 7],
    "user_id": [1, 1, 1, 2, 2, 3, 3],
    "event_time": pd.to_datetime(["2025-03-01 10:00", "2025-03-02 09:00", "2025-03-02 09:00", "2025-03-01 08:00",
                                  "2025-03-05 12:30", "2025-03-06 07:00", "2025-03-04 22:00"]),
    "event_type": ["login", "view_course", "add_to_cart", "login", "purchase", "login", "view_course"]})
```

Return **each user's latest event**, one row per user, with all four columns of `events` (`event_id, user_id, event_time,
event_type`). The latest event is the one with the largest `event_time`; if two events of a user have the same time, the one
with the larger `event_id` wins. Put the SQL in `QUERY`. Row order does not matter.

## Example

User 1 has events 1, 2 and 3. Events 2 and 3 share the time `2025-03-02 09:00`, so the latest is event 3 (the larger id).
User 3's latest is event 6 (6 March), although event 7 has the larger id: **time** decides first.
