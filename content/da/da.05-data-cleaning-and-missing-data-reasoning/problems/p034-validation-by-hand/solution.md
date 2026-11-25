## Approach

Run each rule on the whole table, treat a missing answer as "fine", and invert to get the failing rows. Only rules with
failures appear in the report, so an empty list means "everything passes". The first three labels are read from the
index with the Boolean mask as a NumPy array (so that positions and labels cannot be confused).

## Code

```python
def validate_table(df, rules):
    result = []
    for name, rule in rules.items():
        ok = rule(df).fillna(True).astype(bool)
        bad = ~ok
        if bad.any():
            result.append((name, int(bad.sum()), df.index[bad.to_numpy()][:3].tolist()))
    return result
```

## Complexity

O(rules x rows): each rule is one vectorised pass.

## Another way

Return a DataFrame with one row per rule, including the passing ones (as the chapter does), and a severity column
(`error` or `warning`). The list of failures is easier to test and to use as a guard: `assert not validate_table(...)`.
Pandera (problem p035) does the same job with a better report.
