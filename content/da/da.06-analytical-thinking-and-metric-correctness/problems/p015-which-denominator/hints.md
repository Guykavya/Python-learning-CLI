## Hint 1

First decide which jobs are in the cohort; what is the comparison for the end of the period? Then count four things in
the cohort: all jobs, completed jobs, jobs with a `started_at`, and jobs with an outcome. Which pandas method tells whether a
timestamp exists, and which tests a status against a list?

## Hint 2

```text
start, end = pd.Timestamp(start), pd.Timestamp(end)
cohort = jobs where created_at >= start and created_at < end
completed = number of cohort rows with status "completed"
created   = number of cohort rows
started   = number of cohort rows with started_at not missing
decided   = number of cohort rows whose status is in [completed, cancelled, failed]
ratio(a, b) = a / b, or None when b is 0
```
