# Fix the shortest-job-first scheduler

A build server runs jobs one at a time. To keep developers happy it uses **shortest job first** (chapter section 10), which minimises the total waiting time. A teammate wrote the scheduler; it is in `starter.py`:

```python
def schedule(jobs):
    """jobs: list of (name, duration). Return (names in run order, total waiting time)."""
    ordered = sorted(jobs, key=lambda job: job[1])
    order = []
    total_wait = 0
    elapsed = 0
    for name, duration in ordered:
        order.append(name)
        elapsed += duration
        total_wait = elapsed
    return order, total_wait
```

The order looks right, but the dashboard shows nonsense waiting times:

```python
>>> schedule([("lint", 6), ("test", 8), ("docs", 7), ("fmt", 3)])
(['fmt', 'lint', 'docs', 'test'], 24)        # the starter
(['fmt', 'lint', 'docs', 'test'], 28)        # expected: waits 0 + 3 + 9 + 16
```

1. Trace the loop by hand for the example. What does `total_wait` hold after each job? What should it hold?
2. There are **two** bugs in the three lines inside the loop that deal with time. Find both. (Hint: fixing only one of them gives 52 for the example; why?)
3. Fix the function. Keep the signature.

## Rules for the fixed function

- A job's waiting time is the total duration of the jobs that run **before** it; the first job waits 0. Return the **sum** of all waiting times.
- Jobs with equal durations keep their **input order** (Python's `sorted` is stable, so this already holds).
- Durations are non-negative integers; an empty list returns `([], 0)`. Do not change the list you are given.

## Think about

Why does the waiting time of job `k` use `elapsed` **before** job `k` is added to it?
