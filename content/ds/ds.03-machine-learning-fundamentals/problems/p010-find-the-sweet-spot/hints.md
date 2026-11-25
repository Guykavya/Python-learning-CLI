## Hint 1

What do you loop over, and what do you remember from each pass? What does `min(..., key=...)` or `np.argmin` return on a tie?

## Hint 2

```text
best = None
for d in 1..max_degree:
    fit on train; v = rmse on validation
    if best is None or v < best_v: best, best_v = d, v     # strict < keeps the smaller degree on a tie
return best
```
