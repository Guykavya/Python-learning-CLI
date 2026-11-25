## Approach

Lines carry their own label and colour, so everything needed is on the artists. Names that start with an underscore are matplotlib's convention for "not in the legend", so they are also not worth a label.

## Code

```python
def direct_label(ax):
    legend = ax.get_legend()
    if legend is not None:
        legend.remove()
    for ln in ax.lines:
        label = ln.get_label()
        if label.startswith("_"):
            continue
        x, y = ln.get_xdata()[-1], ln.get_ydata()[-1]
        ax.text(x, y, label, color=ln.get_color(), ha="left", va="center")
    return ax
```

## Complexity

O(lines).

## Another way

`ax.annotate(label, xy=(x, y), xytext=(5, 0), textcoords="offset points")` puts a small gap between the line end and the text; widen the x limit so the name is not cut off.

## Note

For lines that end at nearly the same height the labels collide: nudge them apart, or label a few key lines only.
