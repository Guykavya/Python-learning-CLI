## Hint 1

Each change needs a day and the day before it. `zip(temps, temps[1:])` gives exactly those
neighbour pairs.

## Hint 2

Number the pairs with `enumerate(..., start=2)`: the first pair ends on day 2.

## Hint 3

The format spec `:+d` shows a sign: `f"{4:+d}"` is `+4`. For 0 you need plain `0`, so
choose with a conditional expression. Keep the best rise and its day; replace only when a
change is **strictly** bigger.
