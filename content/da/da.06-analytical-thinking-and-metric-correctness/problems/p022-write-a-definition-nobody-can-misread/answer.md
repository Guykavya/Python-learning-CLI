## Model answer

**Monthly completion rate (v1, owner: operations).** Of the jobs **created** in a month, the share that ended as
`completed`.

- **Numerator:** jobs created in the month whose status is `completed`.
- **Denominator:** jobs created in the month whose status is `completed`, `cancelled` or `failed` (a job that has reached
  an outcome). The numerator is a **subset** of the denominator: every completed job created in the month is also in the
  denominator, so the result is a real share between 0 and 100 percent.
- **Date basis:** `created_at`, so a job stays in the same month for ever. Timestamps are stored in UTC; the month is cut
  in **IST (UTC+05:30)**, because the business works in India.
- **Period:** half-open. February is `2025-02-01 00:00 IST <= created_at < 2025-03-01 00:00 IST`, so a job created exactly
  at the start counts and one created exactly at the end belongs to March.
- **Statuses left out:** `pending` jobs have no outcome yet. Counting them as "not completed" would punish the newest
  month for work that is still going on. This is the immature-cohort rule: the rate is reported for a month only
  when it is mature, for example once the month ended at least 14 days before the data cut, and the pending count is
  shown beside the rate ("798 of 895 decided, 32 pending").
- **Reported as counts:** always "completed / decided", never a bare percentage.

**What the managers did.** One divided completed by all jobs created (including pending and cancelled), the other divided
completed by jobs that had **started**, which hides every cancellation. Possibly they also cut the month in different
time zones. The definition fixes each choice.

**Checklist: your answer should mention**
- [ ] numerator and denominator, with the numerator a subset of the denominator
- [ ] the date basis (created_at or another timestamp, named)
- [ ] the time zone (IST or UTC, named)
- [ ] a half-open period (start included, end excluded)
- [ ] which statuses are in or out of the denominator (pending, cancelled, failed)
- [ ] immature jobs (too recent to have finished) handled by a rule
- [ ] an owner and a version
