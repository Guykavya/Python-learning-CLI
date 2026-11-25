QUERY = """
WITH cohort AS (
  SELECT user_id, channel, date_trunc('month', signup_at)::DATE AS cohort_month FROM users WHERE signup_at < TIMESTAMP '2025-06-01'
),
flagged AS (
  SELECT c.channel,
         EXISTS (SELECT 1 FROM events e WHERE e.user_id = c.user_id AND e.event_type = 'login'
                   AND date_trunc('month', e.event_time)::DATE = CAST(c.cohort_month + INTERVAL 1 MONTH AS DATE)) AS retained
  FROM cohort c
)
SELECT channel, count(*) AS users, count(*) FILTER (WHERE retained) AS retained_m1,
       CASE WHEN count(*) >= 3 THEN count(*) FILTER (WHERE retained) * 1.0 / count(*) END AS m1_retention
FROM flagged GROUP BY channel
""" 
