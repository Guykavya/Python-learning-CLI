QUERY = """
WITH pairs AS (
  SELECT u.user_id, n.day_n,
         EXISTS (SELECT 1 FROM events e WHERE e.user_id = u.user_id AND e.event_type = 'login'
                   AND e.event_time::DATE = u.signup_at::DATE + n.day_n) AS retained
  FROM users u CROSS JOIN (VALUES (1), (7), (30)) AS n(day_n)
  WHERE u.signup_at::DATE + n.day_n <= DATE '2025-07-15'
)
SELECT n.day_n, count(p.user_id) AS eligible_users, count(*) FILTER (WHERE p.retained) AS retained_users,
       count(*) FILTER (WHERE p.retained) * 1.0 / NULLIF(count(p.user_id), 0) AS retention
FROM (VALUES (1), (7), (30)) AS n(day_n) LEFT JOIN pairs p USING (day_n)
GROUP BY n.day_n
""" 
