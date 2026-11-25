# plotly bars, tested by properties

Chapter sections 7 and 9.5. A plotly figure is a tree of objects: `fig.data` holds the traces, `fig.layout` the title and axes. Test it through these **properties**
(`list(fig.data[0].x)`), not through `fig.to_dict()`, where plotly may store arrays in a compact binary form.

Write `px_bars(df)`. `df` has columns `store` and `revenue` (several rows per store). Return a plotly Express figure with:

- **horizontal** bars (`orientation="h"`): revenue summed per store;
- sorted so that the **largest bar is at the top** (plotly draws the first category at the bottom, so give the bars in ascending order);
- the title `Revenue by store`;
- the x axis titled `Revenue (USD)` and the y axis titled `Store`.

## Example

Totals `A = 150, B = 400, C = 220` give `x = [150, 220, 400]` and `y = ['A', 'C', 'B']`.
