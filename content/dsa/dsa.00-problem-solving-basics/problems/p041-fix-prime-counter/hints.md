## Hint 1

Try `a = 7`, `b = 7`. The answer is clearly 1. What does `range(7, 7)` contain? Then try `a = 1`, `b = 1`, and
`a = 25`, `b = 25`, and `a = 4`, `b = 7`. Which ones are wrong, even after you fix the first bug?

## Hint 2

The four bugs are about: (1) which values of `x` the loop visits, (2) when the divisor loop stops, (3) the number 1,
and (4) where `is_prime` is set to `True`. For (4), trace `a = 4`, `b = 7`: after 4 sets `is_prime = False`,
does anything ever set it back to `True` for 5?

## Hint 3

- The outer loop must include `b`: `range(a, b + 1)`.
- For 25, the divisor 5 has `5 * 5 == 25`, so the loop must run while `d * d <= x`.
- 1 has no divisors to find, so the loop leaves `is_prime` as it was. 1 must start as "not prime": for example
  `is_prime = x >= 2`.
- That assignment must be **inside** the outer loop, so every `x` starts fresh.
