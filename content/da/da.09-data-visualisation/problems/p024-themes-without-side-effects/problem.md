# Themes without side effects

Chapter section 5.6. `sns.set_theme(...)` changes matplotlib's **global** settings (`rcParams`) for every chart drawn afterwards, in the whole program.
A function that calls it quietly restyles the charts of everyone else. The clean way is a **context manager**: the style applies inside the `with` block and is
undone when it ends.

Write `themed_chart(df)`. `df` has columns `label` and `value`. Draw a vertical bar chart and return the Figure.

- create the figure inside `with sns.axes_style("whitegrid"), sns.plotting_context("talk"):`;
- the bar chart has a title (`"Value by label"`) and the grid lines of the `whitegrid` style are visible on the y axis;
- the title font is larger than matplotlib's default (the `talk` context);
- **after** the function returns, `matplotlib.rcParams` is **exactly as before**: do not call `sns.set_theme`.

## Example

Calling `themed_chart(df)` twice and then drawing a plain `plt.subplots()` chart gives the plain chart a default look: no grid, default font size.
