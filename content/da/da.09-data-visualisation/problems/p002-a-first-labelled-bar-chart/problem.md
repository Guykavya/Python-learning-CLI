# A first labelled bar chart

Chapter section 3. A chart without a title and an axis label makes the reader guess. Write
`bar_chart(categories, values, title, ylabel)` that draws **one vertical bar per category** and returns the Figure.

- the bars appear **in the order given**, with the category names as x tick labels;
- the bar heights are the values;
- the Axes has the given title and y label;
- return the Figure; do not call `plt.show()`.

```python
fig = bar_chart(["Harbour", "Airport"], [3200, 4100], "Revenue by store", "Revenue (USD)")
```

## Example

For categories `["a", "b", "c"]` and values `[3, 1, 2]` the figure has three bars of heights 3, 1 and 2, in that order.
