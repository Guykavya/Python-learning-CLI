QUERY = """
WITH cohort AS (SELECT user_id, date_trunc('month', signup_at)::DATE AS cohort FROM users),
size AS (SELECT cohort, count(*) AS cohort_size FROM cohort GROUP BY 1),
activity AS (SELECT DISTINCT user_id, date_trunc('month', event_time)::DATE AS m FROM events
             WHERE event_type = 'login' AND event_time < TIMESTAMP '2025-07-01'),
counts AS (
  SELECT c.cohort, date_diff('month', c.cohort, a.m) AS month_number, count(DISTINCT c.user_id) AS active_users
  FROM cohort c JOIN activity a USING (user_id) GROUP BY 1, 2
)
SELECT cohort, month_number, active_users, cohort_size, active_users * 1.0 / cohort_size AS retention
FROM counts JOIN size USING (cohort)
""" 
