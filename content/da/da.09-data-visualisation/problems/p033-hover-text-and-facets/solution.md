## Approach

Plotly Express makes one trace per panel (when there is no colour grouping), puts the `hover_data` columns in `customdata` and refers to them in `hovertemplate` as `%{customdata[0]}`.

## Code

```python
import plotly.express as px


def px_lines(df):
    return px.line(df, x="month", y="revenue", facet_col="store", hover_data=["units"],
                   labels={"revenue": "Revenue (USD)"}, title="Revenue by month")
```

## Complexity

O(n).

## Another way

`hovertemplate` can be written by hand (`fig.update_traces(hovertemplate="%{y:,.0f} USD<br>%{customdata[0]} units")`) for full control of the text.
