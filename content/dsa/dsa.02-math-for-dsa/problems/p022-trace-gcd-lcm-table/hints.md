## Hint 1

Trace `gcd(100, 75)` on paper: `(100, 75) -> (75, 25) -> (25, 0)`. The answer is the `a` when `b` is 0.

## Hint 2

For `(0, 5)`: the loop starts with `b = 5`, so it runs once: `(0, 5) -> (5, 0 % 5) = (5, 0)`. For `(5, 0)` the loop does
not run at all. For `(0, 0)` the loop does not run either.

## Hint 3

The check column is `gcd * lcm == a * b`. When `a` or `b` is 0, both sides are 0, so what does that give? Work out
`(0, 0)` and `(0, 5)` separately: `g * l` and `a * b`.
