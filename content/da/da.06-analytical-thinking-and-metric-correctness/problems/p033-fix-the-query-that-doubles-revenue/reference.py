QUERY = """
WITH paid_per_job AS (
    SELECT job_id, SUM(amount) AS paid
    FROM payments
    GROUP BY job_id
)
SELECT substr(j.created_at, 1, 7)  AS month,
       SUM(j.quote_total)          AS quoted,
       SUM(COALESCE(p.paid, 0))    AS paid
FROM jobs j
LEFT JOIN paid_per_job p ON p.job_id = j.job_id
GROUP BY month
ORDER BY month
"""
