## Hint 1

Look at the indentation of `else:`. It lines up with `for d`, not with `if`. So it is a **loop else**:
it runs only if the inner loop ends normally, without hitting `break`.

## Hint 2

For each `x`, write out `range(2, x)` first. What is `range(2, 1)`? What is `range(2, 2)`? How many times does
an empty loop run, and does it ever `break`?

## Hint 3

For each `x`, find the first `d` (starting at 2) that divides it. If there is one, print `x = d * (x // d)` and
stop the inner loop. If there is none (including when the range is empty), the `else` prints `x is prime`.
