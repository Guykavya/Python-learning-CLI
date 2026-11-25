## Hint 1

`imshow` places cell `(row i, column j)` at x = j and y = i. Which Axes methods set tick positions and their labels? How do you skip a cell that is `NaN`?

## Hint 2

```text
values = pivot.to_numpy(float)
im = ax.imshow(values)
fig.colorbar(im, ax=ax)
ax.set_xticks(range(ncols), pivot.columns); ax.set_yticks(range(nrows), pivot.index)
for i, j: if not isnan: ax.text(j, i, f"{v:.1f}", ha="center", va="center")
```
