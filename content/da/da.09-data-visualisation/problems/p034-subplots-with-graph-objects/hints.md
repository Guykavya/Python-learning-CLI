## Hint 1

`make_subplots` creates the empty grid. Which method adds a trace to a given row and column? Which method of the figure sets the title of one y axis?

## Hint 2

```text
fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=(...))
fig.add_trace(go.Bar(...), row=1, col=1)
fig.add_trace(go.Scatter(..., mode="lines"), row=1, col=2)
fig.update_yaxes(title_text="Revenue (USD)", row=1, col=1)
fig.update_layout(title_text=..., showlegend=False)
```
