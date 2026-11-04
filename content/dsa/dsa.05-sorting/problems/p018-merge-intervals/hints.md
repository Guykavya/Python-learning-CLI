## Hint 1

If the intervals were sorted by start, which single earlier interval (or merged block) could the next one overlap with?

## Hint 2

Keep the current block `[cl, cr]`. For the next interval `(l, r)`: if `l <= cr` extend `cr = max(cr, r)` (use `max`, because the next interval can be nested inside); otherwise print the block and start a new one.

## Hint 3

```
intervals.sort()
cl, cr = intervals[0]
for l, r in intervals[1:]:
    if l <= cr: cr = max(cr, r)
    else: output (cl, cr); cl, cr = l, r
output (cl, cr)
```
