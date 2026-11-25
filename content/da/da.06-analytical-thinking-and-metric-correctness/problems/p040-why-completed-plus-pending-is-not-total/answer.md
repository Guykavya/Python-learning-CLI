## Model answer

**1. Three reasons.** Nothing is missing: the three numbers count three different groups of jobs.

- **Different date bases.** The total places a job by `created_at`, the parts by `started_at`. A job created in January
  and started in February is in the parts but not in the total: it makes the parts **bigger** (+98). A job created in
  late February and started in March is in the total but not in the parts: **smaller** (-87).
- **Statuses that appear in neither part.** `cancelled` (84 jobs) and `failed` (13) are in the total but neither
  "completed" nor "pending": **smaller** (-84 and -13).
- **A status that has no start date.** A pending job has not started, so a filter on `started_at` can never select it.

**2. Why pending is exactly zero.** Pending means "has not started yet", so `started_at` is empty (`NaT`), and a
comparison with `NaT` is false in pandas (and unknown in SQL). The filter "pending and started in February" is
contradictory, so it is empty for every month. It is not a small number; it is a logic error in the definition.

**3. The net gap hides bigger flows.** The gap is 895 - 809 = 86, but it is the sum of four movements:
-87 - 84 - 13 + 98 = -86. Three flows leave and one enters, and the entering 98 cancels part of the 184 that leave. A
smaller net does not mean a smaller problem, and the next month the flows may no longer cancel.

**4. The fix, and what the bridge adds.** Build the dashboard on **one date basis and the complete set of statuses**: if
everything is counted by `created_at`, then completed + cancelled + failed + pending = total, exactly, for any month,
because the statuses partition the jobs. Otherwise rename the numbers ("completed volume by start date") and do not show
a total beside parts that use another basis. A **bridge** lists every effect with its sign and closes to zero; it also
turns "probably timing" into named groups with job ids behind each line, so someone can act on each one.

**Checklist: your answer should mention**
- [ ] different date basis (created against started)
- [ ] cancelled and failed jobs are in the total but in neither part
- [ ] jobs from earlier periods (created in January, started in February)
- [ ] a pending job has no start date, so the pending line is zero
- [ ] the net hides larger flows in both directions
- [ ] one date basis and all statuses make the parts add up
- [ ] a bridge explains each step and closes to zero
