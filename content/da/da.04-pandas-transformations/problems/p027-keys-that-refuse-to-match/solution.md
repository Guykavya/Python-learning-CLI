## Approach

Measure, fix, measure again.

1. The match rate is the mean of a boolean mask: `isin` says, for each left row, whether its key is in the right key
   column; `True` counts as 1. Measured on the raw keys first.
2. Cleaning order matters: `astype(str)` first (an integer column has no `.str` accessor), then `strip` and `upper`.
   Both sides get the same treatment, otherwise you create new mismatches.
3. `assign(**{key: ...})` writes the cleaned column into a **new** frame, using a column name held in a variable.
4. The rows still failing after cleaning give the list to send back; `unique` and `sorted` make it short and stable.

## Code

```python
import pandas as pd


def clean(s):
    return s.astype(str).str.strip().str.upper()


def normalise_keys(left, right, key):
    before = float(left[key].isin(right[key]).mean())
    l2 = left.assign(**{key: clean(left[key])})
    r2 = right.assign(**{key: clean(right[key])})
    found = l2[key].isin(r2[key])
    after = float(found.mean())
    unmatched = sorted(l2.loc[~found, key].unique().tolist())
    return {"left": l2, "right": r2, "match_before": before, "match_after": after, "unmatched": unmatched}
```

## Complexity

O(n + m) for the string cleaning and the two `isin` checks (hash sets).

## Another way

Measure with a merge instead of `isin`: `l2.merge(r2[[key]].drop_duplicates(), on=key, how="left", indicator=True)` and
`(_merge == "both").mean()`. That is the same number and also shows `right_only` keys, the other half of the audit.
Converting the text side to integers (`pd.to_numeric`) is the other route for ids, but it fails on codes such as
`"P001"` and drops leading zeros.
