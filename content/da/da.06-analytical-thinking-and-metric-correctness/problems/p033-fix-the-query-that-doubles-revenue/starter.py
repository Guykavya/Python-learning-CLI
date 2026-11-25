# This query is BUGGY: the joins multiply the rows of a job, so both sums are too big,
# and the inner joins drop the jobs that have no items or no payments. Fix it.
QUERY = """
SELECT substr(j.created_at, 1, 7) AS month,
       SUM(j.quote_total)         AS quoted,
       SUM(p.amount)              AS paid
FROM jobs j
JOIN items i    ON i.job_id = j.job_id
JOIN payments p ON p.job_id = j.job_id
GROUP BY month
ORDER BY month
"""
