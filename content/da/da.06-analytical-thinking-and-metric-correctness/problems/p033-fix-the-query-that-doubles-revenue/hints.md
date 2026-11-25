## Hint 1

How many rows does job 1 have after joining it to `items` (3 lines) and to `payments` (2 payments)? What does `SUM`
then do with its `quote_total`? Do you even need the `items` table to answer the question? Which kind of join keeps a
job that has no payment?

## Hint 2

```text
WITH paid_per_job AS (SELECT job_id, SUM(amount) AS paid FROM payments GROUP BY job_id)   -- one row per job
SELECT month, SUM(quote_total) AS quoted, SUM(COALESCE(paid, 0)) AS paid
FROM jobs LEFT JOIN paid_per_job USING job_id                                              -- jobs stay once
GROUP BY month ORDER BY month
```
