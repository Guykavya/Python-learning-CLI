# Status on a date

Chapter section 9.3. Today's `status` is a snapshot. To know the state of a job **at a given moment** you rebuild it
from the timestamps, with fixed rules. The function `state` below applies the rules in order: the first one that is
true wins. An event at exactly `AT` **has already happened** (`<= AT`).

1. created after `AT` -> `not yet created`
2. cancelled at or before `AT` -> `cancelled`
3. completed at or before `AT` -> `done`
4. started at or before `AT` -> `in progress`
5. otherwise -> `waiting`

Read the program, hand-trace it, and write **every line it prints**, in order, in `answer.txt`. Python prints a
dictionary with `{`, quotes around texts, and `: ` between key and value.

```python
import pandas as pd

AT = pd.Timestamp("2025-02-10 12:00:00")

jobs = pd.DataFrame({
    "job_id": [101, 102, 103, 104, 105, 106],
    "created_at": pd.to_datetime(["2025-02-01 09:00:00", "2025-02-09 18:00:00", "2025-02-10 12:00:00",
                                  "2025-02-10 12:00:01", "2025-02-05 08:00:00", "2025-02-08 10:00:00"]),
    "started_at": pd.to_datetime(["2025-02-10 12:00:00", None, None, None, "2025-02-09 09:00:00", "2025-02-12 09:00:00"]),
    "completed_at": pd.to_datetime(["2025-02-10 15:00:00", None, None, None, "2025-02-10 11:59:00", "2025-02-12 13:00:00"]),
    "cancelled_at": pd.to_datetime([None, "2025-02-10 12:00:00", None, None, None, None]),
})


def state(r):
    if r["created_at"] > AT:
        return "not yet created"
    if pd.notna(r["cancelled_at"]) and r["cancelled_at"] <= AT:
        return "cancelled"
    if pd.notna(r["completed_at"]) and r["completed_at"] <= AT:
        return "done"
    if pd.notna(r["started_at"]) and r["started_at"] <= AT:
        return "in progress"
    return "waiting"


states = jobs.apply(state, axis=1)
for job_id, s in zip(jobs["job_id"], states):
    print(job_id, s)
print(states.value_counts().sort_index().to_dict())
print(sorted(jobs.loc[states.isin(["waiting", "in progress"]), "job_id"].tolist()))
print(int((jobs["completed_at"] > AT).sum()), int(jobs["completed_at"].notna().sum()))
```

Do not run the code before you have written your answer.

## Example

A job created at 08:00, started at 09:00 and completed at 11:00 on the day of `AT = 12:00` is `done`. If its
`completed_at` were 13:00, it would be `in progress`: at 12:00 the completion had not happened yet.

## After you answer

- Why is job 101 `in progress` when its status today is surely `completed`? Which line of the rules decides it?
- Jobs 102 and 101 both have an event at exactly 12:00:00. Why do they end up in different states?
- What would a filter on today's `status` have reported for `AT`? Why is the last line `2 3`, not `0 3`?
