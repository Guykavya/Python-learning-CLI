## Approach

Compute the interval per group with the given function and pass the half-widths as `yerr`. `errorbar` draws a dot and symmetric whiskers; the y axis is set to start at 0 so that the distance of the dots from the baseline is honest.

## Code

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


def mean_ci(x, level=0.95):
    x = np.asarray(x, float)
    se = x.std(ddof=1) / np.sqrt(len(x))
    h = stats.t.ppf((1 + level) / 2, len(x) - 1) * se
    return x.mean(), h


def means_with_ci(df, group, value):
    names, means, halves = [], [], []
    for name, g in df.groupby(group):
        m, h = mean_ci(g[value])
        names.append(str(name))
        means.append(float(m))
        halves.append(float(h))
    fig, ax = plt.subplots()
    ax.errorbar(names, means, yerr=halves, fmt="o", capsize=5)
    ax.set_ylim(bottom=0)
    ax.set_ylabel(value)
    ax.set_title(f"Mean of {value} by {group} (95% CI)")
    return fig
```

## Complexity

O(n).

## Another way

`sns.pointplot(data=df, x=group, y=value, errorbar=("ci", 95))` computes a bootstrap interval; its numbers differ slightly from a t interval.
