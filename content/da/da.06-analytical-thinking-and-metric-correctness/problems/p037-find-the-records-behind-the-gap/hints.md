## Hint 1

What is the grain you need to compare the two tables at: rows, or jobs? How do you subtract two per-job Series when
some jobs exist on one side only (which number should a missing job have)? Which numbers do you need beside the sums to
tell "repeated rows" from "different amount"?

## Hint 2

```text
d_sum, s_sum = amount sum per job_id on each side;   d_rows, s_rows = row count per job_id on each side
diff = d_sum - s_sum with fill_value=0 (a missing job counts as 0)
for each job_id in sorted order with diff != 0:
    label = only in dashboard / only in sql result / repeated rows (different row counts) / amount differs
gap = total of dashboard - total of sql_result;  unexplained = gap - sum(contributions)
```
