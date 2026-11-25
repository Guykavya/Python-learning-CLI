## Hint 1

For one moment `when`, what three questions decide whether a job was open: has it been created, has it been completed,
has it been cancelled? What must be true about a missing completion time? Which comparison operator (`<` or `<=`) puts an
event exactly at `when` on the "already happened" side?

## Hint 2

```text
when = pd.Timestamp(when)
created   = created_at   <= when
done      = completed_at is present  and completed_at <= when
cancelled = cancelled_at is present  and cancelled_at <= when
open_mask = created and not done and not cancelled        # failed jobs: neither time exists, so they stay open
return sorted(int(id) for id in job_id where open_mask)
```
