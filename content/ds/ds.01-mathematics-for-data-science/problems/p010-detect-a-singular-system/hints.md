## Hint 1

After swapping the best pivot to the diagonal, how big is it? If the whole column below the diagonal is 0 (up to rounding), what does that say about the rows?

## Hint 2

```text
tolerance = 1e-12 * max(|A|)
if abs(pivot) < tolerance: raise ValueError("singular matrix ...")
```
Check before you divide by the pivot.
