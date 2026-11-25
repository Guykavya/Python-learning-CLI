QUERY = """
SELECT CAST(d AS DATE) AS day, count(e.event_id) AS logins
FROM generate_series(DATE '2025-06-01', DATE '2025-06-30', INTERVAL 1 DAY) AS t(d)
LEFT JOIN events e ON e.event_type = 'login' AND e.event_time::DATE = CAST(d AS DATE)
GROUP BY 1
""" 
