## Hint 1

What does `x == np.nan` give for any `x`? Which float comparisons does a missing float give `False` for? How is a
comparison with `pd.NA` different? Which values do `sum`, `mean` and `count` use?

## Hint 2

```text
f = 4, 2, NaN, 4, 4, 2
line 1: every == np.nan is False (six False)
line 2: only position 2 is missing
line 3: f > 2 -> True False False True True False   (NaN > 2 is False for floats)
line 4: sum of 5 values = 16, mean = 16 / 5
line 5: value_counts(dropna=False): 4.0 three times, 2.0 twice, NaN once (sorted by count)
g = 4, <NA>, 2 (Int64): comparisons with <NA> give <NA>; bool(<NA>) raises TypeError
count() counts non-missing values, len counts all rows
```
