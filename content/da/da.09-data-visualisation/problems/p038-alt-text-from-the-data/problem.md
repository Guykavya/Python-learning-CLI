# Alt text from the data

Chapter section 8. A reader who cannot see the chart (a screen reader, a printed black-and-white copy) needs the message in words. An **alt text** describes what
the chart is and states its main finding, and it is best **built from the chart's own data**, so that it can never disagree with the picture.

`bar_values(ax)` is given in `starter.py` (it returns `[(label, value)]` of a vertical or horizontal bar chart, as in problem 3). Write `alt_text(fig, what, by)`
for a figure whose first Axes is a bar chart. It returns exactly this sentence:

```text
Bar chart of {what} by {by}. Highest: {name} ({value}). Lowest: {name} ({value}).
```

- `{value}` is written with a thousands separator and no decimals (`4,210`);
- if several bars share the highest (or the lowest) value, name the **first** of them in drawing order;
- a chart with one bar names the same bar as highest and lowest;
- it works for vertical and horizontal bars.

## Example

Bars `Airport 4210, Mall 2800, Campus 1050` with `what="revenue"` and `by="store"` give
`Bar chart of revenue by store. Highest: Airport (4,210). Lowest: Campus (1,050).`
