## Hint 1

How do you turn the column `status` into a share of completed jobs for a group? Try a boolean column (`status == "completed"`)
and think about what its mean is. Which `groupby` gives the rate per technician, and which one per job type and technician?

## Hint 2

```text
rate(group) = mean of (status == "completed") inside the group
overall = rate grouped by tech
by_type = for each job_type: rate grouped by tech
paradox:
    shared = job types where both a and b appear
    if none: False
    a_wins_every_shared_type = all(rate_a > rate_b for each shared type)
    a_loses_overall          = overall[a] < overall[b]
    return both are true
```
