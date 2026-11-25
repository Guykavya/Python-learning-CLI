# Read data back from a figure

Chapter sections 3 and 9.2. Every artist keeps the data it was given, so a test can check *what a chart contains* without looking at pixels.
You will write the two helper functions the later problems rely on.

- `bar_values(ax)` returns a list of `(label, value)` pairs, one per bar, in drawing order.
  - **vertical** bars (`ax.bar`): the label is the x tick label and the value is the bar **height**;
  - **horizontal** bars (`ax.barh`): the label is the y tick label and the value is the bar **width**.
  - Rule for the orientation: the chart is horizontal when all bars have the **same height** and the widths are **not** all equal.
    Otherwise treat it as vertical.
- `line_data(ax, i=0)` returns `(x, y)` of the `i`-th line as two NumPy arrays (`y` as floats).

Call `ax.figure.canvas.draw()` before you read tick labels: until a figure is drawn, matplotlib has not created them.

```python
fig, ax = plt.subplots()
ax.bar(["a", "b"], [3, 1])
bar_values(ax)         # [('a', 3.0), ('b', 1.0)]
```

## Example

`ax.barh(["x", "y", "z"], [5, 0, 2])` gives `[('x', 5.0), ('y', 0.0), ('z', 2.0)]`.
