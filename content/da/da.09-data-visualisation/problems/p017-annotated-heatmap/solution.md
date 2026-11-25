## Approach

`imshow` draws the matrix; the colour bar is a second Axes. Ticks and cell labels use the same coordinates: column `j` is x = `j`, row `i` is y = `i`.

## Code

```python
import numpy as np
import matplotlib.pyplot as plt


def heatmap(pivot):
    values = pivot.to_numpy(dtype=float)
    fig, ax = plt.subplots()
    im = ax.imshow(values)
    fig.colorbar(im, ax=ax)
    ax.set_xticks(range(values.shape[1]), [str(c) for c in pivot.columns])
    ax.set_yticks(range(values.shape[0]), [str(r) for r in pivot.index])
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            if not np.isnan(values[i, j]):
                ax.text(j, i, f"{values[i, j]:.1f}", ha="center", va="center")
    return fig
```

## Complexity

O(rows x columns).

## Another way

`seaborn.heatmap(pivot, annot=True, fmt=".1f")` does all of this; writing it once by hand shows what it does.
