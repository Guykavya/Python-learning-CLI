## Approach

`regplot` fits an ordinary least-squares line (the same as `np.polyfit(x, y, 1)`) and draws it as one `Line2D`. The slope of that line is `(y_last - y_first) / (x_last - x_first)`.
With `ci=None` no bootstrap band is computed, which is faster and removes a source of randomness.

## Code

```python
import matplotlib.pyplot as plt
import seaborn as sns


def trend(df):
    fig, ax = plt.subplots()
    sns.regplot(data=df, x="x", y="y", ci=None, ax=ax)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig
```

## Complexity

O(n) for the fit.

## Another way

`np.polyfit` plus `ax.plot` draws the same line without seaborn: it is how you would check any fitted line you did not draw yourself.
