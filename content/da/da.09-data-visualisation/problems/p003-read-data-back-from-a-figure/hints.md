## Hint 1

What does each bar of `ax.bar` store as its `get_height()`? And what does a bar of `ax.barh` have constant: the height or the width?

## Hint 2

```text
canvas.draw()
patches = ax.patches
horizontal = all heights equal and not all widths equal
horizontal -> labels from get_yticklabels, values = widths
else       -> labels from get_xticklabels, values = heights
```

`line_data`: `ln = ax.lines[i]`, then `np.asarray(ln.get_xdata())` and `np.asarray(ln.get_ydata(), float)`.
