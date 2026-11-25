## Approach

Every check reads a property that the figure already stores. The order of the messages is fixed (Axes first, then fonts) so that tests can compare whole lists. A colour bar is its own Axes and would otherwise be flagged as an untitled, unlabelled chart.

## Code

```python
import matplotlib.text


def lint_figure(fig, min_font=8.0, max_legend=7):
    fig.canvas.draw()
    issues = []
    for i, ax in enumerate(fig.axes):
        if ax.get_label() == "<colorbar>":
            continue
        name = f"axes[{i}]"
        if not ax.get_title():
            issues.append(f"{name}: no title")
        has_data = bool(ax.lines or ax.patches or ax.collections)
        if has_data and not ax.get_xlabel() and not ax.get_ylabel():
            issues.append(f"{name}: no axis labels")
        if ax.patches and not ax.lines:
            heights = {round(p.get_height(), 6) for p in ax.patches}
            widths = {round(p.get_width(), 6) for p in ax.patches}
            horizontal = len(heights) == 1 and len(widths) > 1
            limit = ax.get_xlim()[0] if horizontal else ax.get_ylim()[0]
            if limit > 0:
                issues.append(f"{name}: bar chart value axis starts at {limit:g}, not 0")
        legend = ax.get_legend()
        if legend is not None and len(legend.get_texts()) > max_legend:
            issues.append(f"{name}: legend has {len(legend.get_texts())} entries (more than {max_legend})")
    for t in fig.findobj(matplotlib.text.Text):
        if t.get_visible() and t.get_text().strip() and t.get_fontsize() < min_font:
            issues.append(f"text smaller than {min_font:g} pt")
            break
    return issues
```

## Complexity

O(artists in the figure).

## Another way

The chapter's `lint_figure` adds more rules (a missing legend for several lines, shared-axis labels); a real linter grows with the mistakes you meet, and is tuned until it stops flagging good charts.

## Note

A linter finds mechanical failures. It cannot tell if the chart answers the question or if the title is true: that review stays with a person.
