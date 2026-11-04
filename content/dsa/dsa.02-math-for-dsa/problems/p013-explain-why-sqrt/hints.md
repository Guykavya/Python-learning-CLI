## Hint 1

Suppose `n = a * b` and `a <= b`. What if both `a` and `b` were bigger than `sqrt(n)`? What would `a * b` be?

## Hint 2

If a composite number always has a small divisor `a <= sqrt(n)`, then when you have tested every `i` up to
`sqrt(n)` and found nothing, there is no such `a`, so `n` cannot be composite. For the sieve, think of `2p`,
`3p`, ...: which of these have a smaller prime factor than `p`?

## Hint 3

For `<=` versus `<`: try `n = 9` or `25`. The only divisor in range is exactly `sqrt(n)`.
