## Hint 1

Count the line items per job: how many rows does each job produce after the merge? The row count is their total; the sum of `quote_total` is each quote times its number of lines.

## Hint 2

```text
lines per job: job1 = 3, job2 = 1, job3 = 2, job4 = 1  -> rows = 7
sum after merge = 1000*3 + 400*1 + 700*2 + 300*1
mean after merge = that sum / 7 rows;  true mean = (1000+400+700+300) / 4
drop_duplicates(job_id) keeps one row per job, so the sum is the true one
```
