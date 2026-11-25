## Hint 1

Which seaborn functions return a *context manager* for the style and for the font scale? What is the difference between them and `sns.set_theme`?

## Hint 2

```text
with sns.axes_style("whitegrid"), sns.plotting_context("talk"):
    fig, ax = plt.subplots()
    ax.bar(...)
    ax.set_title("Value by label")
return fig
```

Create the figure **inside** the block; the settings are read when the artists are made.
