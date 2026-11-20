## Hint 1

For `max_lateness`: keep a clock `t`. For each job in the order, add its duration to `t`; that is its finish time. Its lateness is `t - deadline`, but never below 0. Which job's lateness do you report?

## Hint 2

For `best_order`: try three keys on `[(1, 2), (10, 10)]` by hand: shortest first, least slack (`deadline - duration`) first, earliest deadline first. Which ones are optimal? Then think about an **inversion**: two neighbours `a, b` where `a`'s deadline is later than `b`'s. If you swap them, the pair ends at the same time as before. Can the maximum lateness rise?

## Hint 3

```
max_lateness(jobs, order):
    t = 0; worst = 0
    for i in order:
        t += duration of job i
        worst = max(worst, t - deadline of job i)
    return worst

best_order(jobs):
    return the indices 0..n-1 sorted by the job's deadline
```
