## Model answer

1. **`jobs`**: one row per job. Key `job_id`. Shape: entity. Trap: `status` is the *current* state; it changes, so a count
   by status is only true for the moment of the extract.
2. **`items`**: one row per line item inside a job. Key `job_id` + `line_no` (neither alone). Shape: line (detail).
   Trap: a join from `jobs` repeats `quote_total` on every line, so a sum of it is multiplied; and `len` counts lines, not jobs.
3. **`daily_payments`**: one row per day per payment method. Key `day` + `method`. Shape: aggregate (a summary of events).
   Trap: you cannot get distinct customers from it, and summing `total_paid` over days is fine but averaging the daily
   averages is not; a day without payments has no row.
4. **`jobs_by_status_midnight`**: one row per job per midnight snapshot. Key `snapshot_date` + `job_id`. Shape: snapshot.
   Trap: counting rows gives job-days, not jobs; a job that stays open for ten days appears ten times, so use `nunique`.
5. **`job_events`**: one row per event that happened to a job. Key `job_id` + `event` (if each event happens once) or the
   event id. Shape: event. Trap: one job has several rows; counting rows counts events, and the same job is in the
   table as `created` and as `completed`.

**Checklist: your answer should mention**
- [ ] each grain is written as "one row per ..." (a thing, plus a time part where there is one)
- [ ] a composite key for the line table (`job_id` + `line_no`) and for the daily aggregate
- [ ] the shape names: entity, line, aggregate, snapshot, event
- [ ] the snapshot table counts job-days, not jobs (use distinct)
- [ ] a header value repeated on lines (fan-out) or a count of rows that is not a count of jobs
