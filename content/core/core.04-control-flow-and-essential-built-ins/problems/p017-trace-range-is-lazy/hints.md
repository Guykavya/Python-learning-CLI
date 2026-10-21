## Hint 1

`r[i]` is `start + i * step`. `r[-1]` is the last number before the stop.

## Hint 2

`x in r` asks: is `x` within the range's ends, and is `x - start` a multiple of the step?

## Hint 3

`r[1:4]` takes items 1, 2 and 3 of `r` and describes them as a new range with a new start,
stop and the same step. `range(0, 6, 2)` and `range(0, 5, 2)` both produce 0, 2, 4.
