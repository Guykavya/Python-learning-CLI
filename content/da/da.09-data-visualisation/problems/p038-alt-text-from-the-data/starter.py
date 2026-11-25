def bar_values(ax):
    """[(label, value)] for each bar of a vertical or horizontal bar chart (given)."""
    ax.figure.canvas.draw()
    patches = list(ax.patches)
    heights = {round(p.get_height(), 6) for p in patches}
    widths = {round(p.get_width(), 6) for p in patches}
    if len(heights) == 1 and len(widths) > 1:
        labels = [t.get_text() for t in ax.get_yticklabels()]
        return list(zip(labels, [float(p.get_width()) for p in patches]))
    labels = [t.get_text() for t in ax.get_xticklabels()]
    return list(zip(labels, [float(p.get_height()) for p in patches]))


def alt_text(fig, what, by):
    """'Bar chart of {what} by {by}. Highest: {name} ({value}). Lowest: {name} ({value}).' built from the bars."""
    raise NotImplementedError
