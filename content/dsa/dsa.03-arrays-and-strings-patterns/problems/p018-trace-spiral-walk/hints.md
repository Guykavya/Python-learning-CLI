## Hint 1

The first side reads row `top = 0` from column 0 to column 3, then `top` becomes 1. The right side reads column
`right = 3` from row `top = 1` to row `bottom = 2`.

## Hint 2

The bottom side reads row 2 **backwards**: `range(right, left - 1, -1)` with `right = 2` (already shrunk) and
`left = 0`. The left side reads column 0 **upwards** from `bottom` (already shrunk to 1) to `top = 1`.

## Hint 3

The second lap starts with `top = 1, bottom = 1, left = 1, right = 2`: one row, `6 7`. After it, `top = 2` is past
`bottom = 1`. Which `range` calls are now empty, and which `if` is false?
