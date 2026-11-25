## Approach

`ax.bar` takes the category names (placed on the x axis in the order given) and the heights. Title and label belong to the Axes.

## Code

```python
import matplotlib.pyplot as plt


def bar_chart(categories, values, title, ylabel):
    fig, ax = plt.subplots()
    ax.bar(categories, values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    return fig
```

## Complexity

O(n) bars.

## Another way

`ax.set(title=title, ylabel=ylabel)` sets several properties in one call.
