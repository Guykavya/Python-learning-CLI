# Direct labels instead of a legend

Chapter section 8.3. A legend makes the eye travel between the lines and a key. Writing the name **at the end of each line** removes the trip, and
helps readers who cannot tell the colours apart.

Write `direct_label(ax)` for an Axes that has several **labelled** lines and (probably) a legend:

- remove the legend (if there is none, do nothing about it);
- for every line whose label does **not** start with an underscore (matplotlib gives unlabelled lines names like `_child0`), add **one text** with the line's label,
  placed at the line's **last point**, with the **same colour** as the line, left-aligned (`ha="left"`);
- do not draw anything for unlabelled lines (a reference line, a mean line);
- return the Axes.

## Example

Lines labelled `Airport`, `Campus`, `Mall` give three texts at the last points of those lines, in the colours of the lines, and `ax.get_legend()` is `None`.
