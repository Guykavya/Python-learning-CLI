## Approach

Shortest job first (chapter section 10). The adjacent-swap argument: if a longer job `a` runs directly before a shorter job `b`, swapping them leaves everyone outside the pair unchanged (the pair still takes `da + db`), while inside the pair the waiting changes from `da` (for `b`) to `db` (for `a`), which is smaller. So any order with a longer job before a shorter neighbour can be improved, and the sorted order is the best.

```python
def min_total_waiting(durations):
    wait = 0
    elapsed = 0
    for d in sorted(durations):        # shortest job first
        wait += elapsed                # this job waited for everything before it
        elapsed += d
    return wait
```

## Complexity

`O(n log n)` for the sort, `O(n)` for the running sum.

## Another way

Count how often each duration is paid: after sorting, the job at position `i` (0-based) is waited for by the `n - 1 - i` jobs after it, so the total is `sum(d * (n - 1 - i) for i, d in enumerate(sorted(durations)))`. The same formula explains **why** sorting helps: the biggest multipliers go to the smallest durations.
