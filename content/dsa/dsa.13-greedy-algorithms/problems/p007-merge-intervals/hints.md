## Hint 1

If the intervals are sorted by start, can a new interval overlap a block **before** the current one? Every earlier block ended before the current block began, and the new interval starts at or after the current block's start. So you only ever compare with the **last** block of the output.

## Hint 2

For each interval `(s, e)` in sorted order: if the output is not empty and `s <= last block's end`, it overlaps or touches: the block's end becomes the bigger of the two ends. Otherwise it starts a new block `[s, e]`. Why the bigger, and not simply `e`?

## Hint 3

```
out = []
for (s, e) in sorted(intervals):
    if out and s <= out[-1][1]:
        out[-1][1] = max(out[-1][1], e)
    else:
        out.append([s, e])         # a NEW list, not the input's own
return out
```
