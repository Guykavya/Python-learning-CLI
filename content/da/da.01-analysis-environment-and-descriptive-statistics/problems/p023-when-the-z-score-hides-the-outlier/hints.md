## Hint 1

What do the two methods share (indexes of values, a threshold, a rule on every value) and what does each one need to compute first? Why can a single value in a short list never have a z above a certain size (try `n = 8` with one value far away)?

## Hint 2

```text
flag_iqr: q1, _, q3 = quantiles(values, n=4, method="inclusive"); iqr = q3 - q1
          return [i for i, x in enumerate(values) if x < q1 - k*iqr or x > q3 + k*iqr]
flag_z:   mean = fmean; sd = stdev; if sd == 0: return []
          return [i for i, x in enumerate(values) if abs(x - mean) / sd > t]
```
