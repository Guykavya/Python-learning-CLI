# Subplots with graph objects

Chapter section 7. When Plotly Express is not enough, you build the figure from **graph objects** (`go.Bar`, `go.Scatter`) and place them yourself with `make_subplots`.

Write `two_panels(bars, trend)`:

- `bars` is a DataFrame with the columns `label` and `value`; `trend` is a DataFrame with the columns `month` and `revenue`;
- return a figure with **one row and two columns** (`make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=("By store", "Over time"))`);
- left panel: a `go.Bar` of `value` against `label`; right panel: a `go.Scatter` line (`mode="lines"`) of `revenue` against `month`;
- the two panels **share the y axis** (`shared_yaxes=True`), and the y axis is titled **once**, `Revenue (USD)`, on the left panel only;
- the figure has the title `Revenue overview`, and no legend (`showlegend=False`).

The tests read `fig.data[i].xaxis`, `fig.layout.yaxis.title.text`, `fig.layout.yaxis2` and the trace types.

## Example

The bar trace is on `xaxis == "x"` and the line trace on `xaxis == "x2"`.
