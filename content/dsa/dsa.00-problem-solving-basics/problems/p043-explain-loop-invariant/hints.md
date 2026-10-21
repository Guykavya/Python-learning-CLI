## Hint 1

For Loop 1, write the pairs for 252 and 105: (252, 105), (105, 42), (42, 21), (21, 0). Compute the gcd of each pair.
What do you notice? For Loop 2, after reading the first 3 numbers, what does `largest` hold?

## Hint 2

If `d` divides both `a` and `b`, does it divide `a - q * b`? And if `d` divides both `b` and `a - q * b`, does it divide `a`?
So the pairs `(a, b)` and `(b, a % b)` have exactly the same common divisors. For stopping: compare the new `b`
(which is `a % b`) with the old `b`.

## Hint 3

When Loop 1 stops, `b` is 0. What is `gcd(a, 0)`? When Loop 2 stops, every number has been read.
For question 4, try the input `3` numbers: `-5`, `-2`, `-9`.
