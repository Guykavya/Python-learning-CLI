def bar_values(ax):
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
    pairs = bar_values(fig.axes[0])
    hi = max(pairs, key=lambda p: p[1])
    lo = min(pairs, key=lambda p: p[1])
    return f"Bar chart of {what} by {by}. Highest: {hi[0]} ({hi[1]:,.0f}). Lowest: {lo[0]} ({lo[1]:,.0f})."
