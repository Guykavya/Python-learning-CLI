## Hint 1

Reduce `a` and `b` modulo `m` first. Then compute `g = gcd(a, m)`. What does `b % g != 0` tell you?

## Hint 2

If `g` divides `b`, divide `a`, `b`, `m` by `g`. Now `a'` and `m'` are coprime, so `a'` has an inverse modulo `m'`. What is
`x`?

## Hint 3

```
a %= m; b %= m
g = gcd(a, m)                    # gcd(0, m) = m
if b % g != 0: print -1
else:
    a2, b2, m2 = a // g, b // g, m // g
    x = b2 * inverse(a2, m2) % m2        # m2 == 1 gives x = 0
```
