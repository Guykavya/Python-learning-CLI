## Approach

A retention table is easy to misread; the four ideas are cohort, month number, immature cells and weighting.

## Code

There is nothing to run. If you wanted a quick check in SQL, the pooled value for month 1 is the sum of `active_users` over the cohorts that have a month-1 cell divided by the sum of their `cohort_size`:

```sql
SELECT month_number, sum(active_users) * 1.0 / sum(cohort_size) AS pooled_retention
FROM retention_grid WHERE active_users IS NOT NULL GROUP BY 1 ORDER BY 1
```

## Complexity

Not applicable.

## Another way

Compare **columns**, never rows with different observed lengths. A pooled curve is a good summary of "typical retention"; the per-cohort curves tell you whether it is changing. For a "will April's M3 be better?" question the honest answer is "unknown yet", with the M1 comparison as the only evidence.
