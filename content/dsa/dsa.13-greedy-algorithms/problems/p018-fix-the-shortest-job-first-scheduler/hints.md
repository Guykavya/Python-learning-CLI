## Hint 1

Trace the starter on `fmt 3, lint 6, docs 7, test 8`. After each job, write `elapsed` and `total_wait`. You get `total_wait` = 3, 9, 16, 24: the last value simply **replaces** the earlier ones. What operator adds to a total instead of replacing it?

## Hint 2

With `total_wait += elapsed` the trace gives 3 + 9 + 16 + 24 = 52. Those are the **finish** times. `fmt` finishes at 3 but waited 0: when the job's waiting time is added, `elapsed` must not yet include the job itself. Which two lines should change places?

## Hint 3

```
for name, duration in ordered:
    order.append(name)
    total_wait += elapsed      # wait = everything before this job
    elapsed += duration        # then the job runs
```
