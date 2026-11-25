## Hint 1

Which `px.line` arguments produce one panel per value of a column, add a column to the tooltip, and rename a column for display? Where does Plotly keep the extra tooltip values: in `customdata`.

## Hint 2

```text
fig = px.line(df, x="month", y="revenue", facet_col="store", hover_data=["units"],
              labels={"revenue": "Revenue (USD)"}, title="Revenue by month")
```
