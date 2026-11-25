# Fix the query that doubles revenue

Chapter section 10.3. A dashboard query reports, for every month a job was created, the **quoted** value of the jobs and
the **money paid** on them. Both numbers are far too high, and months that have only unpaid jobs are missing. The file
`solution.py` already contains the query. Fix it.

The tables (timestamps are text in the format `YYYY-MM-DD HH:MM:SS`):

```text
jobs(job_id, created_at, status, quote_total)         one row per job
items(job_id, line_no, amount)                        one row per line of a job (a job has 1 to 3 lines)
payments(payment_id, job_id, paid_at, amount)         one row per payment (a job has 0 to 2 payments)
```

The buggy query:

```sql
SELECT substr(j.created_at, 1, 7) AS month,
       SUM(j.quote_total)         AS quoted,
       SUM(p.amount)              AS paid
FROM jobs j
JOIN items i    ON i.job_id = j.job_id
JOIN payments p ON p.job_id = j.job_id
GROUP BY month
ORDER BY month
```

Required result, **one row per month** that has at least one job (month = first 7 characters of `created_at`),
sorted by month, with these columns:

- `month`: text such as `'2025-02'`
- `quoted`: the sum of `quote_total` over the jobs created in that month (each job once)
- `paid`: the sum of the `amount` of all payments of those jobs, `0` when there are none

The query does not need the `items` table at all. The fix is not "add `DISTINCT`": two different jobs can have the same
amounts, and `SUM(DISTINCT x)` would drop one of them.

## Example

One job (`quote_total` 1000) with two lines and two payments (400 and 600) in February gives the buggy query
`quoted = 4000` and `paid = 2000` (the job appears 4 times). The correct row is `('2025-02', 1000, 1000)`.
