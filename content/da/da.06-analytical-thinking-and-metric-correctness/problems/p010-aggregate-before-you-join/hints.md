## Hint 1

What is the grain of `payments`, and what grain do you need before the join with `jobs`? Which one-line `groupby` brings
`payments` to that grain? What happens to a job with no payment after a left join?

## Hint 2

```text
paid_by_job = payments grouped by job_id, sum of amount, named "paid"
per_job = jobs left-merged with paid_by_job on job_id, validate="1:1"
per_job["paid"] = missing -> 0
per customer: groupby customer_id, quoted = sum(quote_total), paid = sum(paid)
convert both columns back to int
```
