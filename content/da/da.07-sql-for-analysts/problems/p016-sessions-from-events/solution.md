## Approach

Flag, number, group. The flag is 1 on the first event of each user and wherever the gap exceeds 30 minutes. The running sum of the flags (with a `ROWS` frame and a tie-break in the `ORDER BY`) is the session number. Then one row per user and session gives the length, and a second aggregation gives the per-user numbers.

## Code

```python
QUERY = """
WITH e AS (
  SELECT user_id, event_id, event_time,
         lag(event_time) OVER (PARTITION BY user_id ORDER BY event_time, event_id) AS prev_time
  FROM events
),
f AS (
  SELECT *, CASE WHEN prev_time IS NULL OR event_time - prev_time > INTERVAL 30 MINUTE THEN 1 ELSE 0 END AS new_session
  FROM e
),
n AS (
  SELECT *, sum(new_session) OVER (PARTITION BY user_id ORDER BY event_time, event_id ROWS UNBOUNDED PRECEDING) AS session_no
  FROM f
),
s AS (
  SELECT user_id, session_no, epoch(max(event_time) - min(event_time)) / 60.0 AS minutes
  FROM n GROUP BY user_id, session_no
)
SELECT user_id, count(*) AS sessions, avg(minutes) AS avg_session_minutes FROM s GROUP BY user_id
"""
```

## Complexity

O(n log n) for the sorts in the two windows.

## Another way

The same recipe splits any ordered sequence into runs: streaks (gap of one day), "visits" to a shop (gap of 2 hours), "bursts" of errors. Only the flag condition changes. A subtle point: use `INTERVAL 30 MINUTE` and `>`: `date_diff('minute', ...)` counts minute **boundaries** and would say 1 minute for 10:00:59 to 10:01:00.

## Pitfall to remember

The session limit is a *definition*. Write it in the metric document: 30 and 60 minutes give different numbers of sessions.
