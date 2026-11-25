## Hint 1

`barh` puts the first bar at the bottom. So if you want the largest at the top, in which order must you give the bars: ascending or descending? (Or is there a way to flip the axis instead?)

## Hint 2

```text
totals = df.groupby(cat)[val].sum().sort_values()     # ascending: the largest is drawn last = on top
fig, ax = plt.subplots()
ax.barh(totals.index, totals.values)
ax.set_xlim(left=0)
ax.set_xlabel(val)
return fig
```
