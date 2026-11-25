# Figure and Axes

Chapter sections 1 and 3. A matplotlib chart lives in a **Figure** (the whole page); the Figure holds one or more **Axes**
(the panels, each with its own x and y axis). `plt.subplots` makes both at once.

Write `make_panels(rows, cols, sharey=False, figsize=(6, 4))`. It creates a grid of empty panels and **returns the Figure**.

- the Figure has `rows * cols` Axes;
- its size in inches is `figsize`;
- when `sharey=True` all panels share one y axis (zooming one zooms them all); when `False` they do not.

Do not call `plt.show()`: return the figure, so that a test (or `savefig`) can use it.

```python
fig = make_panels(2, 3, sharey=True, figsize=(9, 5))
len(fig.axes)             # 6
fig.get_size_inches()     # array([9., 5.])
```

## Example

`make_panels(1, 2)` returns a Figure with two side-by-side Axes whose y axes are independent.
