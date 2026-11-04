**1. A small divisor always exists.** If `n` is composite, write `n = a * b` with `1 < a <= b`. If `a` were larger
than `sqrt(n)`, then `b >= a` would be too, and `a * b > sqrt(n) * sqrt(n) = n`, a contradiction. So the smaller
factor satisfies `a * a <= a * b = n`, that is `a <= sqrt(n)`.

**2. Stopping rule.** Factors come in pairs: if `i` divides `n`, so does `n / i`, and one of the two is at most
`sqrt(n)`. If we test every `i` from 2 up to `sqrt(n)` and none divides `n`, then no pair exists, so `n` has no
divisor except 1 and itself: it is prime. Testing larger `i` could only find the partner of a small divisor we
would already have found.

**3. Examples.** For 91, the loop tries 2, 3, 4, ..., 9 (`9 * 9 = 81 <= 91`, `10 * 10 = 100 > 91`). It stops at
`i = 7` already, because `91 % 7 == 0`. We never need 13, the partner of 7. For 97 the loop tries 2 to 9 (`9 * 9 = 81`),
finds nothing, then `10 * 10 = 100 > 97` ends the loop: prime.

**4. Savings.** For `n = 10^12` (a prime near it) going up to `n - 1` is about 10^12 steps, which is hours or days.
Going up to `sqrt(n) = 10^6` is a million steps: a fraction of a second. The cost drops from O(n) to O(sqrt n).

**5. `<=` matters.** If `n = p * p` is a square of a prime, its only divisor in range is `p` itself, and
`p * p = n`. For `n = 9`: with `i * i < n`, `i = 3` is never tried (`9 < 9` is false), so 9 is wrongly called
prime. Same for 25 and 49.

**6. Sieve.** When we reach prime `p`, a multiple `k * p` with `k < p` has the factor `k`, which has a prime factor
smaller than `p`, so that multiple was already crossed off earlier. The first multiple not yet crossed is
`p * p`. Starting there saves repeated work.
