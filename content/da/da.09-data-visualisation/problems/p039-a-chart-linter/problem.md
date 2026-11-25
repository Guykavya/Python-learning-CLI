# A chart linter

Chapter section 9.3. Some rules apply to every chart, and a program can check them the way a code linter checks style. Write `lint_figure(fig, min_font=8.0, max_legend=7)`.
It returns a **list of strings**, one per problem, empty for a good figure. Call `fig.canvas.draw()` first so that tick labels exist.

For each Axes, in order (index `i` counts the figure's axes, `fig.axes`), **skip colour-bar axes** (`ax.get_label() == "<colorbar>"`) and report, in this order:

1. `axes[i]: no title` when the Axes has no title (`ax.get_title()` empty; a figure-level `suptitle` does not count).
2. `axes[i]: no axis labels` when the Axes has data (lines, patches or collections) and **both** its x label and its y label are empty.
3. `axes[i]: bar chart value axis starts at {limit:g}, not 0` when the Axes has bars (patches, no lines) and its **value axis** lower limit is above 0.
   Vertical bars (the default) use the y axis; horizontal bars (all patches with the same height, different widths) use the x axis.
4. `axes[i]: legend has {n} entries (more than {max_legend})` when the legend exists and has more than `max_legend` entries.

After the Axes, once for the whole figure:

5. `text smaller than {min_font:g} pt` when any visible, non-empty text in the figure (`fig.findobj(matplotlib.text.Text)`) has a font size below `min_font`.

## Example

A bar chart with no title, no labels and an axis from 2.0 gives `['axes[0]: no title', 'axes[0]: no axis labels', 'axes[0]: bar chart value axis starts at 2, not 0']`.
