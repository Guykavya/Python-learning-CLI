## Hint 1

What step does counting up need? Counting down?

## Hint 2

`range` excludes its stop. To include `b`, the stop must be one step **past** `b`: `b + 1`
when going up, `b - 1` when going down.

## Hint 3

`step = 1 if a <= b else -1`, then `range(a, b + step, step)`.
