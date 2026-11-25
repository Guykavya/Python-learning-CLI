## Approach

Put the dates in the index, `resample(freq)` cuts the time line into bins, and `sum` adds each bin. For weekly bins
anchored on Monday (`"W-MON"`) each bin is closed on the right and labelled by its Monday, so a Monday belongs to the
week that ends that day. `"ME"` bins are calendar months labelled by their last day. Empty bins give 0. Passing the
alias through unchanged means pandas 3's `ValueError` for `"M"` reaches the caller, which is what the task asks.

## Code

```python
import pandas as pd


def period_totals(daily, freq):
    s = daily.set_index("date")["revenue"].resample(freq).sum()
    return s.rename_axis("period").reset_index()
```

## Complexity

O(n) over the days.

## Another way

`daily.resample(freq, on="date")["revenue"].sum()` uses a column directly. For months only, a `groupby` on
`daily["date"].dt.to_period("M")` gives the same totals labelled `2025-01` instead of a date, but it drops empty months
that `resample` keeps.
