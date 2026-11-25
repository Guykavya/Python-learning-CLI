QUERY = """
WITH am AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS month FROM events
            WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'),
lagged AS (SELECT user_id, month, lag(month) OVER (PARTITION BY user_id ORDER BY month) AS prev FROM am),
active AS (
  SELECT user_id, month,
         CASE WHEN prev IS NULL THEN 'new' WHEN prev = CAST(month - INTERVAL 1 MONTH AS DATE) THEN 'retained' ELSE 'resurrected' END AS state
  FROM lagged
),
churn AS (
  SELECT a.user_id, CAST(a.month + INTERVAL 1 MONTH AS DATE) AS month, 'churned' AS state
  FROM am a
  WHERE CAST(a.month + INTERVAL 1 MONTH AS DATE) < DATE '2025-07-01'
    AND NOT EXISTS (SELECT 1 FROM am b WHERE b.user_id = a.user_id AND b.month = CAST(a.month + INTERVAL 1 MONTH AS DATE))
)
SELECT * FROM active UNION ALL SELECT * FROM churn
""" 
