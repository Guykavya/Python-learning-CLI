## Hint 1

Which money belongs to the work you finished in the period, and when was it paid: before, inside or after? Which
payments made inside the period belong to jobs that were *not* finished inside it, and how can you split those by the
job's completion date and status? Which seven lines make `work value + steps = net cash`, and what is the sign of each?

## Hint 2

```text
done = completed jobs with completed_at in [start, end);  work_value = sum of their quote_total
p = payments joined to jobs (status, completed_at);  on_done = p.job_id in done
before / inside / after = payments of done jobs by paid_at;  not_paid = work_value - before - inside - after
other = payments inside the period on jobs NOT in done: earlier (completed_at < start),
        later (completed_at >= end or pending), rest
steps = [-before, -after, -not_paid, +earlier, +later, +rest, -refunds_in_period]
closes = work_value + sum(steps) == (cash_gross - refunds)
```
