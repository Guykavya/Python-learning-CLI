# deque: a round-robin scheduler

An operating system shares one CPU between many programs with **round robin**: each job runs for
at most a fixed slice of time (the *quantum*), then goes to the back of the line if it still has
work left. A queue where you take from the front and add to the back is exactly what
`collections.deque` is for: `popleft()` and `append()` are both O(1). (A list's `pop(0)` has to
shift every other element.)

Write in `solution.py`:

`round_robin(jobs: list[tuple[str, int]], quantum: int) -> list[tuple[str, int]]`

- `jobs` is a list of `(name, work)` in arrival order; `work` is how many time units the job needs.
- Repeat until no job is left: take the job at the **front**, run it for `min(quantum, remaining)`
  units and record `(name, units_run)`. If it still has work left, put it at the **back**.
- A job with `work == 0` never runs and records nothing.
- Return the list of recorded slices in order.
- `quantum < 1` raises `ValueError`. Do not change the `jobs` list you were given.

**Example**

```python
round_robin([("A", 5), ("B", 2), ("C", 3)], 2)
# [('A', 2), ('B', 2), ('C', 2), ('A', 2), ('C', 1), ('A', 1)]
```

Step by step: queue `A5 B2 C3`. A runs 2 → `B2 C3 A3`. B runs 2 and is done → `C3 A3`.
C runs 2 → `A3 C1`. A runs 2 → `C1 A1`. C runs 1, done. A runs 1, done.

Also write `finish_order(jobs, quantum) -> list[str]`: the names in the order the jobs
**finish** (for the example: `['B', 'C', 'A']`). Jobs with zero work are not listed.
