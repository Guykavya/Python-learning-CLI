## Hint 1

Which method answers "is each value of this column found in that other column?" What do you get when you negate its result
with `~`? Which column do you want from the rows it selects?

## Hint 2

```text
known = customers["customer_id"]
bad_jobs = jobs rows where NOT jobs.customer_id.isin(known)   -> take job_id
idle     = customers rows where NOT known.isin(jobs.customer_id) -> take customer_id
return {"jobs_without_customer": sorted list of bad_jobs, "customers_without_job": sorted list of idle}
```

Use `.tolist()` so the ids are plain ints.
