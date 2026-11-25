## Hint 1

Write the merged table out on paper first: one row per (job, line). How many rows has job 1, job 2, job 3? That gives the row count and tells you which key columns repeat.

## Hint 2

```text
j      = 6 rows: job 1 x2, job 2 x1, job 3 x3, with city and quote_total repeated on each row
dup(job_id)          -> does any job_id appear twice?
dup(job_id, line_no) -> is the pair repeated?
dup(city, item)      -> do Pune/labour (job 1) and Pune/labour (job 3) both exist?
by_city: Delhi = rows of job 2; Pune = rows of jobs 1 and 3; quote = sum of the repeated quote_total
one: first row of each job_id; sum its quote_total once per job
```
