# Annotate the peak

Chapter section 3.5. A good chart says where to look. Write `annotate_peak(ax, x, y)` for an Axes that already shows the line `y` against `x`.
It adds exactly two things and returns the same Axes:

1. **one annotation** on the highest point, with text `Peak: <max>` where the maximum is written with a thousands separator and no
   decimals (`Peak: 4,210`); the annotation points at `(x at the maximum, the maximum)` (`xy`);
2. **one horizontal line** across the chart at the **mean** of `y` (use `ax.axhline`).

`x` and `y` are lists of the same length. If the maximum occurs more than once, mark the first.

```python
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1000, 4210, 2500])
annotate_peak(ax, [1, 2, 3], [1000, 4210, 2500])
ax.texts[0].get_text()     # 'Peak: 4,210'
```

## Example

For `y = [10, 40, 25, 5]` the annotation points at `(2, 40)` and the horizontal line is at height `20.0`.
