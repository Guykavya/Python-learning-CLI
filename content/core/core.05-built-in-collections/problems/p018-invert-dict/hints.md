## Hint 1

First build `colours = {}` with `colours[key] = value`. Then invert it.

## Hint 2

`{v: k for k, v in colours.items()}` swaps each pair. What happens when the same `v` is assigned twice?

## Hint 3

A dict key keeps its **first** position; assigning to it again only changes its value. So `red`
stays first, but its value ends up as `cherry`.
