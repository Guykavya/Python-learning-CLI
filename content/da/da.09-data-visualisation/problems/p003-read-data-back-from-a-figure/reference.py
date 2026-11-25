import numpy as np


def bar_values(ax):
    ax.figure.canvas.draw()
    patches = list(ax.patches)
    heights = {round(p.get_height(), 6) for p in patches}
    widths = {round(p.get_width(), 6) for p in patches}
    horizontal = len(heights) == 1 and len(widths) > 1
    if horizontal:
        labels = [t.get_text() for t in ax.get_yticklabels()]
        return list(zip(labels, [float(p.get_width()) for p in patches]))
    labels = [t.get_text() for t in ax.get_xticklabels()]
    return list(zip(labels, [float(p.get_height()) for p in patches]))


def line_data(ax, i=0):
    ln = ax.lines[i]
    return np.asarray(ln.get_xdata()), np.asarray(ln.get_ydata(), dtype=float)
