## Approach

`groupby` only knows months that occur. `reindex` against the complete month range inserts the missing months as `NaN`. The plot then breaks the line there.
(`resample("MS").sum()` would put 0 in the gaps, which is a false number.)

## Code

```python
import matplotlib.pyplot as plt
import pandas as pd


def monthly_line(df):
    months = df["date"].dt.to_period("M").dt.to_timestamp()
    m = df.groupby(months)["revenue"].sum()
    m = m.reindex(pd.date_range(m.index.min(), m.index.max(), freq="MS"))
    fig, ax = plt.subplots()
    ax.plot(m.index, m.values)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Revenue")
    return fig
```

## Complexity

O(n + months).

## Another way

`df.set_index("date")["revenue"].resample("MS").sum(min_count=1)` returns `NaN` for months without any row; that is the same idea in one line.
