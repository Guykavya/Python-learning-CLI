## Hint 1

Put the jobs in a `deque` as `[name, remaining]` pairs (or tuples you rebuild). The loop is "while the queue is not empty: take from the left". What decides whether the job goes back in, and at which end?

## Hint 2

`ran = min(quantum, remaining)`. Record `(name, ran)`. The job goes back with `remaining - ran` only if that is still above zero; `append` puts it at the back. Skip zero-work jobs when you build the queue. For `finish_order`, a job finishes exactly on the slice where `remaining - ran == 0`; can you reuse the slices of `round_robin` instead of simulating twice?

## Hint 3

```
round_robin(jobs, quantum):
    if quantum < 1: raise ValueError
    queue = deque((name, work) for name, work in jobs if work > 0)
    slices = []
    while queue:
        name, left = queue.popleft()
        ran = min(quantum, left)
        slices.append((name, ran))
        if left - ran > 0:
            queue.append((name, left - ran))
    return slices
```
For `finish_order`: count each job's remaining work in a dict, walk the slices, subtract, and note the name when it hits 0.
