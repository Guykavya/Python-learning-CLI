def _bars(ax):
    return list(ax.patches)


def visual_change(ax):
    y0 = ax.get_ylim()[0]
    h = [p.get_height() - y0 for p in _bars(ax)]
    return h[1] / h[0] - 1


def lie_factor(ax):
    heights = [p.get_height() for p in _bars(ax)]
    return visual_change(ax) / (heights[1] / heights[0] - 1)


def is_truncated(ax):
    patches = _bars(ax)
    if not patches:
        return False
    heights = {round(p.get_height(), 6) for p in patches}
    widths = {round(p.get_width(), 6) for p in patches}
    if len(heights) == 1 and len(widths) > 1:
        return bool(ax.get_xlim()[0] > 0)
    return bool(ax.get_ylim()[0] > 0)
