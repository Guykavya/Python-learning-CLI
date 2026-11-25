QUERY = """
WITH e AS (
  SELECT user_id, event_id, event_time, lag(event_time) OVER (PARTITION BY user_id ORDER BY event_time, event_id) AS prev_time FROM events
),
f AS (SELECT *, CASE WHEN prev_time IS NULL OR event_time - prev_time > INTERVAL 30 MINUTE THEN 1 ELSE 0 END AS new_session FROM e),
n AS (SELECT *, sum(new_session) OVER (PARTITION BY user_id ORDER BY event_time, event_id ROWS UNBOUNDED PRECEDING) AS session_no FROM f),
s AS (SELECT user_id, session_no, epoch(max(event_time) - min(event_time)) / 60.0 AS minutes FROM n GROUP BY user_id, session_no)
SELECT user_id, count(*) AS sessions, avg(minutes) AS avg_session_minutes FROM s GROUP BY user_id
""" 
