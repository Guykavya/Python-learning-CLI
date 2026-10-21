## Approach

A dict from length to a set of words. The sets remove duplicates; sorting at print time gives
the required order.

## Code

```python
groups = {}
for w in input().split():
    groups.setdefault(len(w), set()).add(w)
for length in sorted(groups):
    print(f"{length}: {' '.join(sorted(groups[length]))}")
```

## Complexity

O(n) to group, plus sorting: O(k log k) for the lengths and for each group's words.
