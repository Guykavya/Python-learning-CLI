## Approach

The reader measures a bar from the bottom of the axis, so the *drawn* height is `height - bottom`. The lie factor compares the visual change with the real change. Orientation is found as in problem 3: horizontal bars share one height and differ in width.

## Code

```python
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
```

## Complexity

O(bars).

## Another way

`lie_factor` (Tufte) is the ratio of the size of an effect shown in the graphic to the size of the effect in the data; here we measure it with heights.

## Note

For a bar chart, "includes 0" is the right test, not "starts at exactly 0": a chart whose axis goes from -5 to 10 shows the whole bar and is honest.
