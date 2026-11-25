## Approach

Relabel last year's values with this year's months, then subtract: pandas aligns by label, so a missing month gives `NaN` instead of silently comparing with the wrong month.

## Code

```python
def yoy_change(series):
    last_year = series.copy()
    last_year.index = last_year.index + 12
    out = series - last_year.reindex(series.index)
    out.name = series.name
    return out
```

## Complexity

O(n).

## Another way

`series.shift(12, freq="M")` on a `PeriodIndex` shifts the **labels** (not positions) and gives the same answer.
