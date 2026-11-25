## Hint 1

The numerator is the same for both: how many line items belong to a job in `jobs`? Which method asks "is this job in that
column?" What are the two different denominators, and which pandas method counts different values?

## Hint 2

```text
n_items     = number of items rows whose job_id is in jobs.job_id
n_jobs      = distinct job_id in jobs
n_customers = distinct customer_id in jobs
items_per_job      = n_items / n_jobs        (None if n_jobs is 0)
items_per_customer = n_items / n_customers   (None if 0)
```

Do not merge: an inner merge would silently drop jobs without lines from the denominator.
