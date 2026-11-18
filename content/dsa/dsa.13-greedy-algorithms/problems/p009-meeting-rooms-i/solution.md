## Approach

Sort by start (chapter section 6). If every meeting ends at or before the next one starts, the meetings form a chain in time and no two can overlap. If some meeting ends after the next one starts, those two clash. So checking neighbours in sorted order is enough.

```python
def can_attend_all(meetings):
    ordered = sorted(meetings)
    for i in range(len(ordered) - 1):
        if ordered[i][1] > ordered[i + 1][0]:     # ends after the next one starts
            return False
    return True
```

## Complexity

`O(n log n)` for the sort and `O(n)` for the check, against `O(n^2)` for all pairs.

## Another way

The one-line version of the chapter: `all(ordered[i][1] <= ordered[i + 1][0] for i in range(len(ordered) - 1))`. Or connect it to activity selection (p002): one person can attend all meetings exactly when the largest non-overlapping set is the whole list, `max_activities(meetings) == len(meetings)`. Or to p010: exactly when one room is enough.
