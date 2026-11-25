## Hint 1

Which function creates a Figure *and* a grid of Axes in one call? Which of its arguments sets the shape, the size and the shared axis?

## Hint 2

```text
fig, axes = plt.subplots(rows, cols, sharey=sharey, figsize=figsize)
return fig
```
