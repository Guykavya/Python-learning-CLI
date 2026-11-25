## Approach

Each rule is a boolean mask; a mask lists the jobs that break the rule. Collect `(job_id, position, label)` triples,
sort them, and drop the position. Sorting by the position of the rule gives the "order of the table" inside one job.
Comparisons with `NaT` are `False`, so a rule about two times is silent when one of them is missing, which is what we
want (the missing-time rules are separate).

## Code

```python
LABELS = [
    "completed without completed_at",
    "completed_at on a non-completed job",
    "cancelled without cancelled_at",
    "cancelled but started",
    "completed before it started",
    "started before it was created",
]


def lifecycle_problems(jobs):
    j = jobs
    masks = [
        j["status"].eq("completed") & j["completed_at"].isna(),
        j["status"].ne("completed") & j["completed_at"].notna(),
        j["status"].eq("cancelled") & j["cancelled_at"].isna(),
        j["status"].eq("cancelled") & j["started_at"].notna(),
        j["completed_at"] < j["started_at"],
        j["started_at"] < j["created_at"],
    ]
    found = []
    for order, (label, mask) in enumerate(zip(LABELS, masks)):
        for job_id in j.loc[mask, "job_id"]:
            found.append((int(job_id), order, label))
    found.sort()
    return [(job_id, label) for job_id, _, label in found]
```

## Complexity

O(6n): six vectorised masks, then a sort of the (usually few) problems.

## Another way

The chapter returns only a **count** per rule (`mask.sum()`). The list of ids is more useful: it is what you hand to the
team that owns the data. A third form is a long DataFrame `(job_id, problem)` built with `pd.concat` of the six filtered
frames; the loop above keeps the sorting rule explicit.
