## Approach

A bar is a `Rectangle` patch. For `ax.bar` the rectangles have one common width and different heights; for `ax.barh` the opposite.
The tick labels carry the category names.

## Code

```python
import numpy as np


def bar_values(ax):
    ax.figure.canvas.draw()
    patches = list(ax.patches)
    heights = {round(p.get_height(), 6) for p in patches}
    widths = {round(p.get_width(), 6) for p in patches}
    horizontal = len(heights) == 1 and len(widths) > 1
    if horizontal:
        labels = [t.get_text() for t in ax.get_yticklabels()]
        return list(zip(labels, [float(p.get_width()) for p in patches]))
    labels = [t.get_text() for t in ax.get_xticklabels()]
    return list(zip(labels, [float(p.get_height()) for p in patches]))


def line_data(ax, i=0):
    ln = ax.lines[i]
    return np.asarray(ln.get_xdata()), np.asarray(ln.get_ydata(), dtype=float)
```

## Complexity

O(n) in the number of bars or points.

## Another way

`ax.containers[0]` is a `BarContainer` holding the same rectangles, which is safer when a chart also contains other patches
(an annotation box, for example).
