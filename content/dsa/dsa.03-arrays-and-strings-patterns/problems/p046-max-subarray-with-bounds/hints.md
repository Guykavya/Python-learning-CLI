## Hint 1

Plain Kadane keeps `cur`, the best sum of a run ending at `i`. Add `cur_start`, the index where that run begins.
When you restart the run at `i`, `cur_start = i`. When you replace the best, copy `cur`, `cur_start` and `i`.
Now: which of the two decisions controls "earliest start", and which controls "shortest"?

## Hint 2

If `cur` is exactly 0, extending it and restarting give the same sum. Extending keeps the **earlier** start, so restart
only when `cur < 0`. If a later run reaches a sum **equal** to the best, it ends later; replacing would make the answer
start later or be longer, so replace only on `>`.

## Hint 3

```
cur = a[0], cur_start = 0
best = a[0], best_l = best_r = 0
for i in 1..n-1:
    if cur >= 0: cur += a[i]
    else:        cur = a[i]; cur_start = i
    if cur > best: best, best_l, best_r = cur, cur_start, i
print best, best_l + 1, best_r + 1
```
