## Approach

Three defects, one root cause: joining two "many" tables to the one-row-per-job table multiplies each job.

1. **Fan-out.** Job 1 has 3 lines and 2 payments, so the joins make 3 x 2 = 6 rows for it. `SUM(j.quote_total)` adds its
   quote 6 times, and each payment 3 times.
2. **Lost jobs.** The inner joins drop jobs with no lines or no payments (job 4, job 5), and with them all of February.
3. **Wrong fix.** `SUM(DISTINCT ...)` would drop job 2, whose quote is the same as job 1's.

The cure is the rule of the chapter: **aggregate, then join**. Reduce `payments` to one row per job in a CTE, `LEFT JOIN`
it to `jobs`, and use `COALESCE(paid, 0)` for jobs without payments. The `items` table is not needed.

## Code

```python
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
```

## Complexity

One pass over `payments` to group, one join on `job_id` (a hash or index lookup per job), one pass to group by month.

## Another way

Two scalar subqueries per job, `(SELECT SUM(amount) FROM payments p WHERE p.job_id = j.job_id)`, give the same
result without a CTE (a correlated subquery; fine for small tables, slower for large ones). Compute `quoted` and `paid`
in two separate queries and join them on `month` if you prefer to keep every query simple.
