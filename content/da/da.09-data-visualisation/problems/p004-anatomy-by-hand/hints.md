## Hint 1

How many Axes does a 2 x 2 grid create? What does `twinx()` do to that number?

## Hint 2

Count per Axes: `plot` adds to `ax.lines`, `bar` adds one rectangle per bar to `ax.patches`. `set_title` belongs to the Axes you call it on, and
a new Axes starts with the empty title `''`.
