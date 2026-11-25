QUERY = """
WITH l AS (SELECT DISTINCT user_id, event_time::DATE AS day FROM events WHERE event_type = 'login'),
bounds AS (SELECT min(day) AS d0, max(day) AS d1 FROM l),
cal AS (SELECT CAST(d AS DATE) AS day FROM bounds, generate_series(d0, d1, INTERVAL 1 DAY) AS t(d))
SELECT c.day,
       count(DISTINCT l.user_id) FILTER (WHERE l.day = c.day) AS dau,
       count(DISTINCT l.user_id) FILTER (WHERE l.day > c.day - 7) AS wau,
       count(DISTINCT l.user_id) AS mau
FROM cal c LEFT JOIN l ON l.day BETWEEN c.day - 29 AND c.day
GROUP BY c.day
""" 
