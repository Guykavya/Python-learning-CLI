import numpy as np
import matplotlib.pyplot as plt


def bubble_sizes(values, max_area):
    v = np.asarray(values, dtype=float)
    if (v < 0).any():
        raise ValueError("negative value")
    top = v.max() if len(v) else 0.0
    if top == 0:
        return np.zeros_like(v)
    return max_area * v / top


def bubble_chart(x, y, values, max_area=400):
    fig, ax = plt.subplots()
    ax.scatter(x, y, s=bubble_sizes(values, max_area), alpha=0.6)
    return fig
