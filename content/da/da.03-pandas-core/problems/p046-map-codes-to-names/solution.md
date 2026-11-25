## Approach

`map` does the lookup but cannot tell "unknown code" from "missing code": both give `NaN`. The difference is in the input: an unknown code is a value that **exists** (`notna()`) but has no result. Build that mask, put `"Other"` there with `where`, and collect the sorted distinct unknown codes from the input.

## Code

```python
def map_regions(s, mapping):
    mapped = s.map(mapping)
    is_unknown = s.notna() & mapped.isna()
    names = mapped.where(~is_unknown, "Other")
    return names, sorted(s[is_unknown].unique().tolist())
```

## Complexity

O(n) lookups, plus O(u log u) to sort the u distinct unknown codes.

## Another way

`s.map(mapping).fillna("Other")` is shorter but turns missing codes into "Other" as well: that is wrong when the difference matters. Alternatively `s.replace(mapping)` leaves unknown codes **unchanged** instead of making them NaN, which can hide them in the output.
