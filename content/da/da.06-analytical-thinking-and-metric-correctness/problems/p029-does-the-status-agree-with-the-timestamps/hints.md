## Hint 1

Write each rule as one boolean mask over the whole table first (a Series of `True`/`False`), using `.eq`, `.ne`,
`.isna()` and `.notna()` and `&`. What does a comparison like `completed_at < started_at` give when one side is `NaT`?
Then ask: how do you turn six masks into one sorted list of pairs?

## Hint 2

```text
LABELS = [six labels in the order of the table]
masks  = [same six boolean Series, same order]
found = []
for position, (label, mask) in enumerate(zip(LABELS, masks)):
    for job_id in jobs.loc[mask, "job_id"]:
        found.append((int(job_id), position, label))
found.sort()                     # by job_id, then by the rule's position
return [(job_id, label) for job_id, position, label in found]
```
