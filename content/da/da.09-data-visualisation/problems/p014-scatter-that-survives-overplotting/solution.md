## Approach

Overplotting is a function of how many points share the same space, so the settings depend on `n`. `alpha` makes overlapping dots add up to a darker colour; a small `s` reduces overlap in the first place.

## Code

```python
import matplotlib.pyplot as plt


def overplot_scatter(df, xlabel, ylabel):
    n = len(df)
    alpha, size = (0.2, 6) if n > 2000 else (0.8, 30)
    fig, ax = plt.subplots()
    ax.scatter(df["x"], df["y"], s=size, alpha=alpha)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig
```

## Complexity

O(n).

## Another way

For hundreds of thousands of points, `ax.hexbin(x, y)` (counts per hexagon) or a 2-D histogram replaces the dots completely.
