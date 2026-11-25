## Approach

One branch per strategy, each a single pandas method that returns a **new** Series. `s.median()` skips missing values by itself, so it is the median of the known values. `ffill` and the default `interpolate` already leave a leading gap untouched, so the edge rule costs no code. A final `raise` covers unknown words.

## Code

```python
def fill_gaps(s, how):
    if how == "drop":
        return s.dropna()
    if how == "zero":
        return s.fillna(0)
    if how == "ffill":
        return s.ffill()
    if how == "interpolate":
        return s.interpolate()
    if how == "median":
        return s.fillna(s.median())
    raise ValueError(f"unknown strategy {how!r}")
```

## Complexity

Each strategy is one pass over the Series: O(n) (the median needs an O(n) selection or O(n log n) sort).

## Another way

A dictionary of functions, `{"drop": lambda s: s.dropna(), ...}`, removes the `if` chain and lets you list the valid words in the error message: `raise ValueError(f"how must be one of {sorted(table)}")`. Which strategy is *right* is a question for da.05: `zero` is wrong for temperatures but right for "no discount".
