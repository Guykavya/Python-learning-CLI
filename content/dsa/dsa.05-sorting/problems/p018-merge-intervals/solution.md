## Approach

Sort by start, then sweep once while keeping a current block. Extend the block when the next start is `<=` the block's end, else close it.

## Code

```python
n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
intervals.sort()
cl, cr = intervals[0]
out = []
for l, r in intervals[1:]:
    if l <= cr:
        cr = max(cr, r)
    else:
        out.append((cl, cr))
        cl, cr = l, r
out.append((cl, cr))
for l, r in out:
    print(l, r)
```

## Complexity

O(n log n) for the sort, O(n) for the sweep, O(n) memory.

## Another way

Sweep line: turn each interval into events `(l, +1)` and `(r, -1)`, sort the events, and open/close blocks when the depth goes from 0 to 1 and back. Needs care at touching points (process `+1` before `-1`).
