# Job sequencing with deadlines

You have a list of jobs. Each job takes exactly **one time unit**, has a **deadline** and a **profit**. Time slots are numbered `1, 2, 3, ...`; a job with deadline `d` earns its profit only if it runs in one of the slots `1 .. d`. Only one job can run in a slot. Jobs you do not run (or that cannot fit) earn nothing.

Write `max_profit(jobs)`. `jobs` is a list of `(deadline, profit)` pairs. Return the **largest total profit** you can earn.

This is the job-sequencing problem of chapter section 10. There are two greedy ways to solve it in the chapter: profit order with the **latest free slot**, or deadline order with a **min-heap** of profits. Either one is fine.

## Example

```python
>>> max_profit([(2, 100), (1, 19), (2, 27), (1, 25), (3, 15)])
142
>>> max_profit([(1, 5), (1, 9), (1, 3)])     # only slot 1 exists: take the 9
9
>>> max_profit([])
0
```

In the first example the best plan runs the 27 job in slot 1, the 100 job in slot 2 and the 15 job in slot 3: `27 + 100 + 15 = 142`. The 19 and 25 jobs both need slot 1, which is already used by a more valuable job.

## Constraints

- `0 <= len(jobs) <= 2000`.
- `1 <= deadline <= 10**9`, `1 <= profit <= 10**6`. Deadlines can be far bigger than the number of jobs.
- Do not change the caller's list.

## Think about

A job with deadline 1,000,000,000 among 5 jobs: how many slots can ever be used? What does that tell you about the size of a `slot` list?
