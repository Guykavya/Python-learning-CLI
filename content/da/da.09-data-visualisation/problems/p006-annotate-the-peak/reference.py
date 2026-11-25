import numpy as np


def annotate_peak(ax, x, y):
    y = np.asarray(y, dtype=float)
    i = int(np.argmax(y))
    ax.annotate(f"Peak: {y[i]:,.0f}", xy=(x[i], y[i]), xytext=(10, -20),
                textcoords="offset points", arrowprops={"arrowstyle": "->"})
    ax.axhline(float(y.mean()), linestyle="--", linewidth=1)
    return ax
