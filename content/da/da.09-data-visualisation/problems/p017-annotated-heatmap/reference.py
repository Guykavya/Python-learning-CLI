import numpy as np
import matplotlib.pyplot as plt


def heatmap(pivot):
    values = pivot.to_numpy(dtype=float)
    fig, ax = plt.subplots()
    im = ax.imshow(values)
    fig.colorbar(im, ax=ax)
    ax.set_xticks(range(values.shape[1]), [str(c) for c in pivot.columns])
    ax.set_yticks(range(values.shape[0]), [str(r) for r in pivot.index])
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            if not np.isnan(values[i, j]):
                ax.text(j, i, f"{values[i, j]:.1f}", ha="center", va="center")
    return fig
