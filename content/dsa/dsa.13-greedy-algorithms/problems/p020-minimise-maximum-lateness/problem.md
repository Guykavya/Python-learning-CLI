# Minimise maximum lateness

One machine must run **every** job, one after another, starting at time 0 and with no gaps. Job `i` is a pair `(duration, deadline)`. If a job finishes at time `f`, its **lateness** is `max(0, f - deadline)`. We want an order that makes the **largest** lateness as small as possible (chapter section 10, "Minimising the maximum lateness").

Write two functions:

1. `max_lateness(jobs, order)`: `order` is a list of job indices (a permutation of `0 .. n-1`). Run the jobs in that order and return the largest lateness (`0` if nobody is late, and `0` for no jobs).
2. `best_order(jobs)`: return an order (a list of indices) whose maximum lateness is as small as possible. If several orders are equally good, return any of them.

## Example

```python
>>> jobs = [(5, 5), (1, 6)]
>>> max_lateness(jobs, [1, 0])       # job 1 ends at 1, job 0 ends at 6: one unit late
1
>>> max_lateness(jobs, [0, 1])       # ends at 5 and 6: nobody late
0
>>> best_order(jobs)
[0, 1]
>>> jobs = [(3, 6), (2, 8), (1, 9), (4, 9), (3, 14), (2, 15)]
>>> max_lateness(jobs, best_order(jobs))
1
```

## Constraints

- `0 <= len(jobs) <= 10**4`, `1 <= duration <= 1000`, `0 <= deadline <= 10**7`.
- Do not change the caller's list.

## Think about

The rule you need ignores the durations completely. Why can a long job with a distant deadline wait, however long it is? And why is "least slack first" (`deadline - duration`, smallest first) **not** the same rule?
