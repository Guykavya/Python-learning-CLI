## Approach

Three rules explain every line: `NaN` equals nothing (so `== np.nan` is `False` everywhere); a float comparison with a
missing value is `False`, but a nullable `Int64` comparison is `<NA>` ("unknown"); aggregations skip missing values
(5 values, not 6).

1. `f == np.nan`: six `False`.
2. `isna()`: `True` only at position 2.
3. `f > 2`: `[True, False, False, True, True, False]`; `NaN > 2` is `False`.
4. `sum` = 4 + 2 + 4 + 4 + 2 = 16.0, `mean` = 16 / **5** = 3.2.
5. `value_counts(dropna=False)`: 4.0 three times, 2.0 twice, NaN once.
6. `g > 2`: `[True, <NA>, False]`.
7. `g == pd.NA`: `<NA>` for every row. Comparing with `pd.NA` never gives True, so it cannot find missing values either.
8. `bool(pd.NA)` raises `TypeError` ("boolean value of NA is ambiguous").
9. `g.sum()` is 6, `g.mean()` is 3.0 (skips the missing value).
10. `f.count()` is 5 (non-missing), `len(f)` is 6.

## Output

```text
[False, False, False, False, False, False]
[False, False, True, False, False, False]
[True, False, False, True, True, False]
16.0 3.2
{4.0: 3, 2.0: 2, nan: 1}
[True, <NA>, False]
[<NA>, <NA>, <NA>]
TypeError
6 3.0
5 6
```

(Hand-traced first, then run on pandas 3.1.1: both agree.)

## Another way

To find missing values always use `isna()` / `notna()`. To use an `Int64` comparison as a mask, write
`(g > 2).fillna(False)` and decide on purpose what "unknown" means.
