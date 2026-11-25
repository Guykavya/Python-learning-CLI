# Detect a truncated axis

Chapter section 6.1. The **length** of a bar is the data. If the value axis does not start at 0, the bottom of every bar is cut off, and small differences look big.
Write three small checks that work on any bar chart (an `Axes`):

- `visual_change(ax)`: the change from the **first bar to the second bar as the eye sees it**, measuring each height **from the bottom of the axis**
  (`ax.get_ylim()[0]`): `h2 / h1 - 1`, where `h = bar height - ylim bottom`.
- `lie_factor(ax)`: `visual_change / data_change`, where `data_change = height2 / height1 - 1` from the raw bar heights (1.0 means honest).
- `is_truncated(ax)`: a plain Python `bool` (not a NumPy `bool_`): `True` when the value axis of a bar chart **does not include 0**. For vertical bars look at the bottom of the y axis; for horizontal bars (all bars the same
  height, different widths) look at the left end of the x axis. An Axes without bars is **not** truncated (a line chart may start above 0).

## Example

Bars 2.108 and 2.344 (an 11.2% growth) on an axis from 2.0 to 2.4: `visual_change` is about `2.185` (219%), `lie_factor` about `19.5`, `is_truncated` is `True`.
On an axis from 0 the same bars give `0.112`, `1.0` and `False`.
