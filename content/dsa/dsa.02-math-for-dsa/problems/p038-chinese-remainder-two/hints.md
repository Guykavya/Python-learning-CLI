## Hint 1

First, solve the easy case by hand: `x = 2 (mod 3)` and `x = 3 (mod 5)`. List `2, 5, 8, 11, ...` and see which is 3 modulo 5.
Now why is that too slow for `m1 = 10^9`?

## Hint 2

Substitute `x = a1 + m1 * k`. What congruence in `k` do you get modulo `m2`? Which earlier problem solves it, and
when does it have no solution?

## Hint 3

```
g = gcd(m1, m2)
if (a2 - a1) % g != 0: print -1
else:
    m2g = m2 // g
    k = ((a2 - a1) // g) * inverse(m1 // g, m2g) % m2g      # m2g == 1 gives k = 0
    x = a1 + m1 * k
```
Python's `%` is non-negative, so a negative `a2 - a1` is fine.
