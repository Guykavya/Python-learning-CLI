## Approach

Uniqueness of each key column gives the relationship. `isin` with the other table's key column gives a True/False per
row; negating and summing counts the orphan **rows**. `NaN` is never "in" another column, so missing keys are counted.

## Code

```python
def relationship(left, right, left_key, right_key):
    left_unique = bool(left[left_key].is_unique)
    right_unique = bool(right[right_key].is_unique)
    kind = {(True, True): "1:1", (True, False): "1:m",
            (False, True): "m:1", (False, False): "m:m"}[(left_unique, right_unique)]
    left_orphans = int((~left[left_key].isin(right[right_key])).sum())
    right_orphans = int((~right[right_key].isin(left[left_key])).sum())
    return {"relationship": kind, "left_orphans": left_orphans, "right_orphans": right_orphans}
```

## Complexity

Two hash lookups of every row: O(n + m).

## Another way

`left.merge(right, on=..., how="outer", indicator=True)` labels each row `left_only`, `right_only` or `both`; but an outer
merge on a non-unique key multiplies rows, so counting orphans from it needs `drop_duplicates` first. `isin` avoids that.
