## Hint 1

For one threshold, how do you count the four cells with NumPy in one line each? Then loop over the grid and keep the cheapest.

## Hint 2

```text
best_t, best_c = None, inf
for t in grid:
    pred = p >= t
    c = tn*cost.get("tn",0) + fp*cost.get("fp",0) + fn*cost.get("fn",0) + tp*cost.get("tp",0)
    if c < best_c: best_t, best_c = t, c
return float(best_t)
```
