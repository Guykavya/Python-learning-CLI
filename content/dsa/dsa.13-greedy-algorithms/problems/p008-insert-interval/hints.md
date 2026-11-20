## Hint 1

You could append `new` and call `merge` from p007: correct, but it sorts again, `O(n log n)`. The list is already sorted. Walk it once and split it into three groups: blocks completely **before** `new`, blocks that **overlap or touch** `new`, and blocks completely **after** it.

## Hint 2

"Before" means the block **ends** before `new` starts: `end < new_start` (strictly, because touching merges). "Overlaps or touches" means the block **starts** at or before `new`'s end: `start <= new_end`. While absorbing, grow `new`: its start becomes the smaller start and its end the bigger end. Append `new` once, after the middle group, then copy the rest.

## Hint 3

```
ns, ne = new
out = []; i = 0
while i < n and intervals[i].end < ns:   out.append(copy of intervals[i]); i += 1
while i < n and intervals[i].start <= ne:
    ns = min(ns, intervals[i].start); ne = max(ne, intervals[i].end); i += 1
out.append([ns, ne])
while i < n:                             out.append(copy of intervals[i]); i += 1
return out
```
