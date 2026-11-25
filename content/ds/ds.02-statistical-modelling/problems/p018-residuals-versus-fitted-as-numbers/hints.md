## Hint 1

Why can you not just compare the first half and the second half of the data? What must the groups be ordered by?

## Hint 2

```text
f = fittedvalues; r = resid
lo, hi = quantile(f, [1/3, 2/3])
top = r[f >= hi]; bottom = r[f <= lo]
return std(top, ddof=1) / std(bottom, ddof=1)
```
