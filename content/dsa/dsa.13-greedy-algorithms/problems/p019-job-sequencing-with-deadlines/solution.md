## Approach

Consider the jobs from the most profitable down. Each job goes into the **latest free slot** at or before its deadline; if every such slot is taken, skip it.

- **Why profit order?** Exchange argument: if an optimal plan skips the most valuable job `x` that could be placed, while it runs a cheaper job `y` in a slot `x` could use, swap `y` for `x`. The plan stays valid and the profit does not drop.
- **Why the latest slot?** An early slot can be used by every job, a late slot only by jobs with late deadlines. Taking the latest allowed slot keeps the scarce early slots for jobs that need them.

With `n` jobs, at most `n` slots are ever used, and a job with deadline above `n` can always use slot `n` or earlier. So the slot list has length `n + 1`, never `max(deadline) + 1` (a deadline of `10**9` would ask for a billion slots).

```python
def max_profit(jobs):
    n = len(jobs)
    free = [True] * (n + 1)                    # free[1..n]; slot 0 is unused
    total = 0
    for deadline, profit in sorted(jobs, key=lambda j: -j[1]):
        for t in range(min(deadline, n), 0, -1):   # latest free slot first
            if free[t]:
                free[t] = False
                total += profit
                break
    return total
```

## Complexity

Sorting is `O(n log n)`. The slot search is `O(n)` per job in the worst case: `O(n^2)` overall, which is fine for `n = 2000`. Space `O(n)`.

## Another way

The heap version from chapter section 10 runs in `O(n log n)` and does not need slots at all:

```python
import heapq

def max_profit(jobs):
    heap = []                                  # profits of the jobs we plan to run
    for deadline, profit in sorted(jobs):      # by deadline
        heapq.heappush(heap, profit)
        if len(heap) > deadline:               # more jobs than slots 1..deadline
            heapq.heappop(heap)                # drop the least profitable
    return sum(heap)
```

It is correct because after each step the heap holds the best set of jobs that can all meet their deadlines among the jobs seen so far. It gives the total but not the slots. A union-find over slots (dsa.12 section 9) gives both in `O(n log n)`.
