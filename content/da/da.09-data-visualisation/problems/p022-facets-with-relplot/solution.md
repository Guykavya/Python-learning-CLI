## Approach

One call creates the figure, the panels and the lines. `set_titles("{col_name}")` replaces `store = A` by `A`. The grid shares the y axis only if `sharey` is true; writing it out shows the choice (panels with different scales are one of the misleading charts of section 6.8).

## Code

```python
import seaborn as sns


def store_lines(df):
    g = sns.relplot(data=df, x="week", y="revenue", col="store", col_wrap=3, kind="line",
                    errorbar=None, facet_kws={"sharey": True})
    g.set_titles("{col_name}")
    return g
```

## Complexity

O(n).

## Another way

Build the panels by hand with `plt.subplots(2, 3, sharey=True)` and a loop over `df.groupby("store")`: more lines, full control of every Axes.
