# Sessions from events

Chapter section 4.9. A **session** is a burst of activity: events with no pause longer than a limit. SQL has no session
function, so we build it in three steps: **flag** where a session starts (the gap to the previous event is too long, or there
is no previous event), **number** the sessions with a running sum of the flags, **group** by user and session number.

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
    "user_id": [1, 1, 1, 1, 1, 2, 3, 3],
    "event_time": pd.to_datetime(["2025-03-01 10:00", "2025-03-01 10:20", "2025-03-01 10:50", "2025-03-01 11:30",
                                  "2025-03-01 11:35", "2025-03-01 12:00", "2025-03-01 09:00", "2025-03-02 09:00"]),
    "event_type": ["login", "view_course", "add_to_cart", "view_course", "checkout_start", "login", "login", "login"]})
```

Use **all** events of a user (any `event_type`). A new session starts when the gap to the user's previous event is **more
than 30 minutes** (a gap of exactly 30 minutes stays in the same session). Return one row per user:

| column | meaning |
|---|---|
| `user_id` | the user |
| `sessions` | number of sessions of the user |
| `avg_session_minutes` | average session length, where a session's length is the time from its first to its last event, in minutes (a one-event session is 0) |

Put the SQL in `QUERY`. Row order does not matter.

## Example

User 1: events at 10:00, 10:20, 10:50 (gaps of 20 and 30 minutes: same session, length 50), then 11:30 (gap 40: **new** session)
and 11:35 (gap 5). Two sessions of 50 and 5 minutes, so `sessions = 2` and `avg_session_minutes = 27.5`. User 3 has two events a
day apart: two sessions of 0 minutes.
