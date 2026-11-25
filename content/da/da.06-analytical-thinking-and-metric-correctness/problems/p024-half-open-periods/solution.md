## Approach

Two comparisons joined with `&`: `s >= start` keeps the start instant, `s < end` rejects the end instant. Comparing
`NaT` gives `False`, so a missing time is never in a period, without any special code. Converting the ends with
`pd.Timestamp(...)` lets the caller pass texts.

## Code

```python
import pandas as pd


def in_period(s, start, end):
    return (s >= pd.Timestamp(start)) & (s < pd.Timestamp(end))
```

## Complexity

O(n) for n timestamps: two vectorised comparisons.

## Another way

`s.between(start, end, inclusive="left")` does the same in one call. Avoid the default `between`: it includes both
ends, which is the closed interval that loses the end of the last day (see problem 25).
