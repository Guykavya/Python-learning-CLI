## Hint 1

For `x^2` at 1 the forward difference is exactly `2 + h` (before rounding). So the truncation error is `h`. Which of the three labels does `0.1` get? `1e-5`?

## Hint 2

For `h = 1e-8` the truncation error is `1e-8` and the rounding error is about `1e-8` too: still below `1e-7`. For `h = 1e-15` the numbers `1 + h` and `1` are almost the same double, so the quotient is badly wrong.
