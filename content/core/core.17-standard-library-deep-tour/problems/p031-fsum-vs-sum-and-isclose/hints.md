## Hint 1

Adding `0.1` ten times rounds ten times. The errors do not cancel: the loop ends just *below*
1.0. What does `print` show for the float just below 1.0? `fsum` rounds once at the end: the exact
sum of ten stored `0.1`s is a hair above 1, and the nearest float to that is exactly `1.0`.

## Hint 2

For `F`: `0.1 + 0.2` is a single `+`, and one `+` is already correctly rounded. Can `fsum` do any
better with only two numbers? What is `0.1 + 0.2` (line `E`) compared with the float `0.3`?

## Hint 3

For `G`, `H` and `K` use the formula: `abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)`.
With `b = 0.0` and `abs_tol = 0.0`, the right side is `1e-09 * 1e-12`. For `I`, do the loop by
hand: `0.0 + 1e16`, then `+ 1.0` (lost), then `- 1e16`.

## Hint 4

`L`: is the stored 2.675 a bit above or a bit below the halfway point? `M`: `floor` goes down,
`ceil` goes up, and `round` sends exact halves to the even integer: -0.5 -> 0, 1.5 -> 2, 2.5 -> 2.
