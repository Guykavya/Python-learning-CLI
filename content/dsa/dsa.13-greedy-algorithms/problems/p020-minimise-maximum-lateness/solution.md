## Approach

`max_lateness` is a direct simulation. Start `worst` at 0, so that early jobs (negative `t - deadline`) count as "not late".

`best_order` is **earliest deadline first (EDF)**: sort the indices by deadline, ignoring durations.

```python
def max_lateness(jobs, order):
    t = 0
    worst = 0
    for i in order:
        duration, deadline = jobs[i]
        t += duration                      # finish time of job i
        worst = max(worst, t - deadline)
    return worst


def best_order(jobs):
    return sorted(range(len(jobs)), key=lambda i: jobs[i][1])
```

**Why EDF is optimal (adjacent swap, chapter section 10).** Take any order. If two neighbours `a, b` have `deadline(a) > deadline(b)`, swap them. The pair ends at the same time `T` as before, and nothing outside the pair moves. `b` now finishes earlier, so its lateness cannot rise. `a` now finishes at `T`, which is when `b` finished before; since `a`'s deadline is later than `b`'s, `a`'s new lateness `T - deadline(a)` is at most `b`'s old lateness `T - deadline(b)`. So the maximum does not rise. Repeating removes every inversion and ends at the EDF order, which is therefore at least as good as any order, including an optimal one.

## Complexity

`max_lateness` is `O(n)`. `best_order` is `O(n log n)` for the sort. Space `O(n)`.

## Another way

Sort the jobs themselves together with their index: `[i for _, i in sorted((d, i) for i, (_, d) in enumerate(jobs))]`. On equal deadlines it puts the smaller index first; any order of equal deadlines is optimal, because swapping two jobs with equal deadlines never changes the maximum (the same swap argument with `deadline(a) = deadline(b)`).
