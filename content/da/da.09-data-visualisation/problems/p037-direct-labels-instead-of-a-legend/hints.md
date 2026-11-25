## Hint 1

Which `Line2D` method gives the colour, the label, and the data? How do you take away a legend that exists, without failing when there is none?

## Hint 2

```text
legend = ax.get_legend(); if legend: legend.remove()
for ln in ax.lines:
    if label starts with "_": continue
    x, y = last point of ln
    ax.text(x, y, label, color=ln.get_color(), ha="left", va="center")
return ax
```
