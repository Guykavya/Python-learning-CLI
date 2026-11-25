## Hint 1

Which function gives the quartiles? After you have the fences, which values are inside, and which of those inside is the lowest and which the highest?

## Hint 2

```text
x = sorted array of floats
q1, med, q3 = np.percentile(x, [25, 50, 75])
lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
inside = x[(x >= lo) & (x <= hi)]
whisker_low, whisker_high = inside.min(), inside.max()
outliers = x[(x < lo) | (x > hi)]
```
