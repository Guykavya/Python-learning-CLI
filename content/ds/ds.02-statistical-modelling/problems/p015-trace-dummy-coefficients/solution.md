## Walk-through

Common part: `10.20 + 0.025 * 10 = 10.45`.

- Delhi (baseline, `get` returns 0.0): 10.450
- Mumbai: 10.45 + 0.12 = 10.570
- Pune: 10.45 - 0.10 = 10.350

Mumbai minus Pune = 0.12 - (-0.10) = 0.22.

## Another way

The same table with `pd.get_dummies(..., drop_first=False)` would need a dummy for every city and no intercept; the baseline-plus-differences layout is what formulas produce by default.
