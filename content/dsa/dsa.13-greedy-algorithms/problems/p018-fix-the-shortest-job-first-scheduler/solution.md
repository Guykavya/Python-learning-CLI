## What is wrong

Two bugs in the loop body:

1. `total_wait = elapsed` **replaces** the total with the current time instead of adding to it. At the end it holds the finish time of the last job (24), not a sum.
2. `elapsed += duration` runs **before** the job's wait is counted, so each job is charged for its own duration too. That counts **finish** times: after fixing only bug 1 the result is `3 + 9 + 16 + 24 = 52`.

The sort was right: shortest job first is the greedy order proved by the adjacent swap in chapter section 10.

## The fix

```python
def schedule(jobs):
    ordered = sorted(jobs, key=lambda job: job[1])
    order = []
    total_wait = 0
    elapsed = 0
    for name, duration in ordered:
        order.append(name)
        total_wait += elapsed          # this job waited for everything before it
        elapsed += duration            # then it runs
    return order, total_wait
```

Trace: `fmt` waits 0 (elapsed becomes 3), `lint` waits 3 (elapsed 9), `docs` waits 9 (elapsed 16), `test` waits 16. Total 28.

## Complexity

`O(n log n)` for the sort, `O(n)` for the loop.

## Another way

Compute the total separately from the order: `durations = [d for _, d in ordered]`, then `sum(d * (len(durations) - 1 - i) for i, d in enumerate(durations))`: each duration is waited for by every job after it. Also note the relation: total finish time = total waiting time + sum of durations (52 = 28 + 24), a quick sanity check for a dashboard.
