## Approach

One call: two keys, two directions. `na_position="last"` is the default but stating it documents the rule (and it applies to descending sorts too: missing values do **not** jump to the top). Sorting by several columns is already stable in pandas; `kind="stable"` makes the promise visible. The returned frame is new, so the input is untouched, and the original labels stay.

## Code

```python
def rank_sellers(df):
    return df.sort_values(["revenue", "seller"], ascending=[False, True],
                          na_position="last", kind="stable")
```

## Complexity

O(n log n) comparisons.

## Another way

Sort twice with stable sorts, least important key first: `df.sort_values("seller").sort_values("revenue", ascending=False, kind="stable")`. That is how multi-key sorting works underneath, and it is the trick to use when one key must be sorted by a rule `sort_values` cannot express (a custom order for the names, for example via `key=`).
