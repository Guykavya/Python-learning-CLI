## Approach

Rebuild the state from the event times, never from `status`. A job is open at `when` if its creation has happened and
neither ending event has happened yet. Writing "present and `<= when`" for each ending event keeps `NaT` from
accidentally counting (a comparison with `NaT` is `False` anyway; the explicit `.notna()` makes the intent visible).
Failed jobs have neither ending time, so they stay open forever: the answer is an upper bound, as the chapter says.

## Code

```python
import pandas as pd


def pending_on(jobs, when):
    when = pd.Timestamp(when)
    created = jobs["created_at"] <= when
    done = jobs["completed_at"].notna() & (jobs["completed_at"] <= when)
    cancelled = jobs["cancelled_at"].notna() & (jobs["cancelled_at"] <= when)
    return sorted(int(j) for j in jobs.loc[created & ~done & ~cancelled, "job_id"])
```

## Complexity

O(n) for the masks, O(k log k) to sort the k open jobs.

## Another way

With an **event table** (one row per status change: `job_id, status, changed_at`) you would take, for each job, the
last event with `changed_at <= when` (`merge_asof`, or sort and `groupby().last()`). That removes the failed-job
guesswork. Snapshots lose history; event logs keep it.
