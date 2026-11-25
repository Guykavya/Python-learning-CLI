## Hint 1

How do you ask pandas "which values are below 0"? What does `s < 0` give for a missing value in a float column, and what
does it give in an `Int64` column? How do you combine "below the low bound" and "above the high bound" into one Boolean
Series, and what must you do when a bound is `None`?

## Hint 2

```text
flags = empty frame with df.index
for column, (low, high) in rules.items():
    bad = Series of False
    if low is not None:  bad = bad | (s < low)   # missing -> False (use fillna(False) for Int64)
    if high is not None: bad = bad | (s > high)
    flags[column] = bad
    counts[column] = int(bad.sum())
return flags, counts
```
