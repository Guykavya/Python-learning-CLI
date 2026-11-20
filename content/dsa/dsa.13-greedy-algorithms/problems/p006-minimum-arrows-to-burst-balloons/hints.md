## Hint 1

Look at the balloon that **ends first**. Some arrow must hit it, so that arrow is somewhere in `[start, end]` of that balloon. Moving it right, up to `end`, can only hit **more** of the other balloons (they all end at or after it). So where should the first arrow go?

## Hint 2

Sort by end. Keep `shot_at`, the position of the last arrow. A balloon is already burst exactly when its start is `<= shot_at` (it ends at or after `shot_at`, because of the sort). Otherwise shoot a new arrow at its end.

## Hint 3

```
arrows = 0
shot_at = -infinity
for (s, e) in balloons sorted by end:
    if s > shot_at:          # strictly: touching is still hit
        arrows += 1
        shot_at = e
return arrows
```
