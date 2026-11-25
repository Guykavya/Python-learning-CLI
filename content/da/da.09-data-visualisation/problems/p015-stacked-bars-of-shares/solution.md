## Approach

Reshape to a wide table, divide each row by its total, then draw one `ax.bar` call per part. `bottom` is the height already used by the earlier parts, so the segments pile up. Each call adds a legend entry in drawing order.

## Code

```python
import numpy as np
import matplotlib.pyplot as plt


def share_bars(df, group, part, value):
    groups = list(df[group].unique())
    parts = list(df[part].unique())
    tbl = (df.groupby([group, part])[value].sum().unstack(fill_value=0)
             .reindex(index=groups, columns=parts, fill_value=0))
    pct = tbl.div(tbl.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots()
    bottom = np.zeros(len(groups))
    for p in parts:
        ax.bar([str(g) for g in groups], pct[p].to_numpy(), bottom=bottom, label=str(p))
        bottom = bottom + pct[p].to_numpy()
    ax.set_ylabel("Share (%)")
    ax.legend()
    return fig
```

## Complexity

O(n + groups * parts).

## Another way

`pct.plot(kind="bar", stacked=True)` does the same in one line, but the explicit `bottom` loop shows what a stacked bar is.

## Note

Sorting `groupby` output would reorder the groups alphabetically; `reindex` to the first-appearance order keeps the order the problem asks for.
