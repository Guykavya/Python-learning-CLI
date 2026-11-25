## Approach

`make_subplots` allocates the axes (`x`/`y` and `x2`/`y2`); `add_trace(..., row, col)` attaches each trace to one of them. With `shared_yaxes=True`, plotly makes `yaxis2` follow `yaxis` (`matches="y"`), so the title is set only on the first.

## Code

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def two_panels(bars, trend):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=("By store", "Over time"))
    fig.add_trace(go.Bar(x=list(bars["label"]), y=list(bars["value"])), row=1, col=1)
    fig.add_trace(go.Scatter(x=list(trend["month"]), y=list(trend["revenue"]), mode="lines"), row=1, col=2)
    fig.update_yaxes(title_text="Revenue (USD)", row=1, col=1)
    fig.update_layout(title_text="Revenue overview", showlegend=False)
    return fig
```

## Complexity

O(n).

## Another way

Build each panel as its own Plotly Express figure and copy its traces into a `make_subplots` grid with `add_trace(trace, row, col)`: you keep Express's defaults and still control the layout.
