## Approach

`stat="density"` scales each bar so that the total area (width x height) is 1. `common_norm=False` applies that to each hue separately; the default `True` would make
the **sum over all groups** equal 1, and a small group would look tiny.

## Code

```python
import matplotlib.pyplot as plt
import seaborn as sns


def hist_by_group(df):
    fig, ax = plt.subplots()
    sns.histplot(data=df, x="value", hue="group", stat="density", common_norm=False, ax=ax)
    return fig
```

## Complexity

O(n).

## Another way

`sns.kdeplot(..., common_norm=False)` draws smooth curves instead of bars; the same argument matters. For an exact comparison without bins, use overlaid ECDFs.

## Note

Pass the arguments explicitly even when they match the defaults of your version: seaborn changes defaults between releases.
