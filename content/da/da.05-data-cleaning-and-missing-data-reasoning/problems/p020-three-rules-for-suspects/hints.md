## Hint 1

For each rule, which two or three numbers do you need first, and which pandas methods give them (`quantile`, `mean`,
`std`, `median`)? Do those methods skip missing values? How do you combine "below the lower fence" and "above the upper
fence" into one Boolean Series? What does a comparison with a missing value give? What happens in `flag_mad` when the MAD
is 0, and what should you return?

## Hint 2

```text
flag_iqr: q1, q3 = x.quantile([.25, .75]); spread = q3 - q1
          return (x < q1 - k*spread) | (x > q3 + k*spread)
flag_z:   return ((x - x.mean()) / x.std()).abs() > t
flag_mad: med = x.median(); mad = (x - med).abs().median()
          if mad is 0 or missing: return a Series of False with x's index
          return (0.6745 * (x - med) / mad).abs() > t
```
Comparisons with a missing value are `False`, so missing values are never flagged.
