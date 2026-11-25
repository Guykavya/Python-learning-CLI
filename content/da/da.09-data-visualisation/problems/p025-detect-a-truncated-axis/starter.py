def visual_change(ax):
    """Change from the first to the second bar as drawn: heights measured from the bottom of the y axis, h2 / h1 - 1."""
    raise NotImplementedError


def lie_factor(ax):
    """visual_change(ax) divided by the real change (height2 / height1 - 1)."""
    raise NotImplementedError


def is_truncated(ax):
    """True when a bar chart's value axis does not include 0 (False when there are no bars)."""
    raise NotImplementedError
