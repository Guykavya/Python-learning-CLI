QUERY = """
WITH v AS (SELECT user_id, min(event_time) AS t_view FROM events WHERE event_type = 'view_course' GROUP BY user_id),
x AS (
  SELECT v.user_id,
         EXISTS (SELECT 1 FROM events p WHERE p.user_id = v.user_id AND p.event_type = 'purchase'
                   AND p.event_time BETWEEN v.t_view AND v.t_view + INTERVAL 7 DAY) AS converted
  FROM v WHERE v.t_view + INTERVAL 7 DAY <= TIMESTAMP '2025-07-15'
)
SELECT count(*) AS eligible_users, count(*) FILTER (WHERE converted) AS converted_users,
       count(*) FILTER (WHERE converted) * 1.0 / NULLIF(count(*), 0) AS conversion_rate
FROM x
""" 
