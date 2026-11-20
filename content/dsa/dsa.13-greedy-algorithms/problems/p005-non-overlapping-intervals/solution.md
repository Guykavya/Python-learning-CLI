## Approach

The fewest removals leave the largest set of non-overlapping intervals, so `removals = n - (largest non-overlapping set)` (chapter section 5). The largest set is activity selection: sort by end time and keep each interval that starts at or after the end of the last kept one.

```python
def min_removals(intervals):
    kept = 0
    last_end = float("-inf")
    for s, e in sorted(intervals, key=lambda iv: iv[1]):
        if s >= last_end:              # keep it: it fits after the last kept interval
            kept += 1
            last_end = e
    return len(intervals) - kept
```

## Complexity

`O(n log n)` for the sort and `O(n)` for the sweep; `O(n)` extra space for the sorted copy.

## Another way

Count removals directly: sort by **start**, keep `prev_end`. When the next interval overlaps (`s < prev_end`), one of the two must go: count a removal and keep the one that **ends earlier** (`prev_end = min(prev_end, e)`), because it blocks less of the future. Otherwise move on with `prev_end = e`. Same exchange argument, written as "drop the later end".
