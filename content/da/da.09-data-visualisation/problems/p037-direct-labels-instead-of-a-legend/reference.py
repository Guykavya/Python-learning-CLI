def direct_label(ax):
    legend = ax.get_legend()
    if legend is not None:
        legend.remove()
    for ln in ax.lines:
        label = ln.get_label()
        if label.startswith("_"):
            continue
        x, y = ln.get_xdata()[-1], ln.get_ydata()[-1]
        ax.text(x, y, label, color=ln.get_color(), ha="left", va="center")
    return ax
