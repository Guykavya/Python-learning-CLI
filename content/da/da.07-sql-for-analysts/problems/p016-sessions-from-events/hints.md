## Hint 1

Three steps, each with a name: which window function gives the time of the previous event? How do you turn the gap into a 0/1 flag for "a new session starts here"? Then which running window turns flags into session numbers 1, 2, 3, ...?

## Hint 2

```text
e : SELECT user_id, event_time, lag(event_time) OVER (PARTITION BY user_id ORDER BY event_time, event_id) AS prev
f : SELECT *, CASE WHEN prev IS NULL OR event_time - prev > INTERVAL 30 MINUTE THEN 1 ELSE 0 END AS new_session
n : SELECT *, sum(new_session) OVER (PARTITION BY user_id ORDER BY event_time, event_id ROWS UNBOUNDED PRECEDING) AS session_no
s : GROUP BY user_id, session_no -> length = max(event_time) - min(event_time) in minutes
final: per user, count(*) sessions and avg(length)
```

Use seconds for the length: `epoch(max(t) - min(t)) / 60.0`.
