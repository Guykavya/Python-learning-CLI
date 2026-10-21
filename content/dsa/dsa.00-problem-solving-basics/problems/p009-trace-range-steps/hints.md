## Hint 1

`range(start, stop, step)` starts at `start` and keeps adding `step`. Is `stop` itself ever included?

## Hint 2

With a positive step, the range keeps going while the value is *less than* `stop`. With a negative step, it keeps going while the value is *greater than* `stop`. If the start already fails that test, the range is empty.

## Hint 3

For `G`, list every value of `i` from `range(3, -4, -2)` and count them. After a `for` loop ends, the loop variable keeps the last value it was given.
