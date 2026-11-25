## Approach

`plt.subplots(rows, cols, sharey=..., figsize=...)` returns the Figure and the Axes. We only need the Figure: `fig.axes` lists the panels.

## Code

```python
import matplotlib.pyplot as plt


def make_panels(rows, cols, sharey=False, figsize=(6, 4)):
    fig, _axes = plt.subplots(rows, cols, sharey=sharey, figsize=figsize)
    return fig
```

## Complexity

O(rows * cols) objects are created.

## Another way

`fig = plt.figure(figsize=figsize)` followed by `fig.subplots(rows, cols, sharey=sharey)` does the same. The `Figure` constructor
(`matplotlib.figure.Figure`) avoids pyplot's global list of open figures, which is better inside a long-running program.
