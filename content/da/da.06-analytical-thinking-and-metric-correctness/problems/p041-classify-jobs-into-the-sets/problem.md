# Classify jobs into the sets

Chapter section 12. For February 2025 the dashboard compares three groups of jobs:

- `T` : created in February (`[1 Feb, 1 Mar)`), any status
- `C` : status `completed` and **started** in February
- `P` : status `pending` and **started** in February

A job that is in exactly one of `T` and `C` gets a reason from the chapter's two rules, copied in the code below
(`why_only_T`, `why_only_C`). Read the program, hand-trace it, and write **every line it prints**, in order, in
`answer.txt`. A line for a job is `<job_id> <sets> <reason>`: `<sets>` lists the sets the job is in, separated by commas
without spaces (`-` when it is in none), and the reason is empty for a job that is in both sets, in neither, or only in `P`
(the line then has no trailing space).

```python
import pandas as pd

S, E = pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01")

jobs = pd.DataFrame({
    "job_id": [201, 202, 203, 204, 205, 206, 207],
    "status": ["completed", "cancelled", "completed", "completed", "pending", "failed", "pending"],
    "created_at": pd.to_datetime(["2025-02-03 09:00:00", "2025-02-05 09:00:00", "2025-01-31 23:59:59",
                                  "2025-02-27 09:00:00", "2025-02-12 09:00:00", "2025-02-14 09:00:00",
                                  "2025-01-20 09:00:00"]),
    "started_at": pd.to_datetime(["2025-02-04 09:00:00", None, "2025-02-01 00:00:00",
                                  "2025-03-01 00:00:00", None, "2025-02-15 09:00:00",
                                  "2025-02-09 09:00:00"]),
})


def month(s):
    return (s >= S) & (s < E)


def why_only_T(r):
    if r["status"] == "cancelled": return "cancelled (never started)"
    if r["status"] == "failed": return "failed"
    if r["status"] == "pending": return "pending (no start date yet)"
    if r["started_at"] >= E: return "started in March or later"
    return "other"


def why_only_C(r):
    if r["created_at"] < S: return "created in January, started in February"
    return "other"


in_T = month(jobs["created_at"])
in_C = month(jobs["started_at"]) & jobs["status"].eq("completed")
in_P = month(jobs["started_at"]) & jobs["status"].eq("pending")

for i, r in jobs.iterrows():
    sets = [name for name, m in (("T", in_T), ("C", in_C), ("P", in_P)) if m[i]]
    reason = ""
    if in_T[i] and not in_C[i]:
        reason = why_only_T(r)
    elif in_C[i] and not in_T[i]:
        reason = why_only_C(r)
    print(f"{int(r['job_id'])} {','.join(sets) or '-'} {reason}".rstrip())

print(sorted(jobs.loc[in_T, "job_id"].tolist()))
print(sorted(jobs.loc[in_C, "job_id"].tolist()))
print(int(in_T.sum()), int(in_C.sum()), int(in_P.sum()), int((in_T & in_C).sum()))
print(len(jobs[in_T & ~in_C]) - len(jobs[in_C & ~in_T]))
```

Do not run the code before you have written your answer.

## Example

A completed job created on 10 February and started on 11 February is in `T` and in `C` (not in `P`), so its line is
`300 T,C`. A job created on 3 February whose status is `cancelled` is in `T` only, and its line is
`301 T cancelled (never started)`.

## After you answer

- Job 203 was created one second before February and started at the first instant of February. Which of the two boundaries decides that it is in `C` and not in `T`?
- Job 204 is `completed` and created in February, yet it is not in `C`. Which boundary rule puts its start in March?
- Job 207 is in `P` only. Why can job 205, also pending, never be in `P`?
- The last line is `3`: how does it relate to the net gap `len(T) - len(C)`, and why is it smaller than the number of jobs that left `T`?
