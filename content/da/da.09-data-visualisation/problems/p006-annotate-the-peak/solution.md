## Approach

`np.argmax` returns the position of the first maximum. `ax.annotate` creates a text object (stored in `ax.texts`) with an optional arrow;
`ax.axhline(value)` adds a `Line2D` whose y data are both equal to `value`.

## Code

```python
import numpy as np


def annotate_peak(ax, x, y):
    y = np.asarray(y, dtype=float)
    i = int(np.argmax(y))
    ax.annotate(f"Peak: {y[i]:,.0f}", xy=(x[i], y[i]), xytext=(10, -20),
                textcoords="offset points", arrowprops={"arrowstyle": "->"})
    ax.axhline(float(y.mean()), linestyle="--", linewidth=1)
    return ax
```

## Complexity

O(n).

## Another way

`ax.text(x[i], y[i], ...)` writes text without an arrow; use `annotate` when the label must sit away from the point.
