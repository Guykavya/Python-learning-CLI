# Hover text and facets

Chapter section 7. In an interactive chart the reader moves the mouse over a point and reads its details. In Plotly Express, `hover_data` adds extra columns to that
tooltip, and `facet_col` splits the data into small multiples.

Write `px_lines(df)`. `df` has the columns `month`, `store`, `revenue` and `units`. Return a `px.line` figure with:

- `x = month`, `y = revenue`, one panel per store (`facet_col="store"`);
- the extra column `units` in the tooltip (`hover_data=["units"]`);
- the revenue labelled with its unit: `labels={"revenue": "Revenue (USD)"}`, so the tooltip and the axis say `Revenue (USD)`;
- the title `Revenue by month`.

The test reads, for each trace, `customdata` (the extra tooltip columns) and `hovertemplate` (the tooltip text pattern).

## Example

Two stores give **two traces** (one per panel); the first trace's `customdata` holds that store's `units` in the row order of the data.
