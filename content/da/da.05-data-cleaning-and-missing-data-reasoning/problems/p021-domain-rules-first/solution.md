## Approach

One pass over the rules. For each column start with "nothing is impossible", then switch on the rows below the low bound
and above the high bound (when the bound exists). Comparisons keep the inclusive rule for free: `<` and `>` do not flag
the bound itself. A missing value compares as `False` in a float column; in a nullable `Int64` column the comparison
gives `<NA>`, so `fillna(False)` makes the answer explicit.

## Code

```python
import pandas as pd


def flag_impossible(df, rules):
    flags = pd.DataFrame(index=df.index)
    counts = {}
    for col, (lo, hi) in rules.items():
        s = df[col]
        bad = pd.Series(False, index=df.index)
        if lo is not None:
            bad = bad | (s < lo).fillna(False).astype(bool)
        if hi is not None:
            bad = bad | (s > hi).fillna(False).astype(bool)
        flags[col] = bad
        counts[col] = int(bad.sum())
    return flags, counts
```

## Complexity

O(rows x rules): one or two vectorised comparisons per rule. No Python loop over rows.

## Another way

`~s.between(lo, hi)` is shorter when both bounds exist, but it flags missing values and cannot express `None`. A
version that uses `s.lt(lo)` and `s.gt(hi)` is the same idea with method names.
