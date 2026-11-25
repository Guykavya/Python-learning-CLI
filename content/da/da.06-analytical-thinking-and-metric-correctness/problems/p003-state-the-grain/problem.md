# State the grain

Chapter sections 2.1 and 2.3. "You must be able to write the grain sentence **before** you compute anything." Practise it
on five tables of QuickFix and its neighbours.

For each description below, write in `answer.md`:

- the **grain sentence** ("one row per ..."),
- the **key** (the column or columns that identify a row),
- the **shape** from section 2.3 (entity, event, line, snapshot, or aggregate),
- one **trap** when you count or sum it.

1. `jobs`: columns `job_id, customer_id, created_at, status, quote_total`.
2. `items`: columns `job_id, line_no, item, amount`, where a job has one to five lines.
3. `daily_payments`: columns `day, method, total_paid, n_payments`, one line for each day and payment method.
4. `jobs_by_status_midnight`: columns `snapshot_date, job_id, status`, a copy of every open job's status taken each midnight.
5. `job_events`: columns `job_id, event_time, event` with values such as `created`, `started`, `completed`.

Aim for about 200 words in total.

## Example

For `customers (customer_id, city, segment)`: "One row per customer. Key: `customer_id`. Shape: entity. Trap: customers
change city over time, so a count by city today is not a count by city last year."
