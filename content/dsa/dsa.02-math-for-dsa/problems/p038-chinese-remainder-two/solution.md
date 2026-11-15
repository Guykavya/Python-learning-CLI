## Approach

Let `g = gcd(m1, m2)`. A common solution must satisfy `a1 = a2 (mod g)`, since both `a1` and `a2` equal `x` modulo a divisor of
`g`. If `g` does not divide `a2 - a1`, there is no solution. Otherwise, substituting `x = a1 + m1*k` gives
`m1*k = a2 - a1 (mod m2)`. Divide by `g`: `(m1/g)*k = (a2-a1)/g (mod m2/g)`, and `m1/g` and `m2/g` are coprime, so `k` is the
product of `(a2-a1)/g` and the inverse of `m1/g` modulo `m2/g`. Because `k < m2/g` and `a1 < m1`, `x = a1 + m1*k < m1 * m2/g = lcm`, so it is the smallest solution.

For the example `2 3 3 5`: `g = 1`, `k = (3-2) * inverse(3, 5) % 5 = 1 * 2 = 2` (since `3*2 = 6 = 1`), `x = 2 + 3*2 = 8`.

Check `1 4 3 6`: `g = 2`, `a2 - a1 = 2`, divisible by 2. `m2/g = 3`, `m1/g = 2`, `inverse(2, 3) = 2`, `k = 1 * 2 % 3 = 2`,
`x = 1 + 4*2 = 9`, and `lcm = 12`, so `x = 9`: `9 % 4 = 1` and `9 % 6 = 3`.

For `1 4 2 6`: `g = 2`, `a2 - a1 = 1`, not divisible by 2: `-1`. (A number `= 1 (mod 4)` is odd; a number `= 2 (mod 6)` is even.)

## Code

```python
def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


q = int(input())
for _ in range(q):
    a1, m1, a2, m2 = [int(x) for x in input().split()]
    g, u, v = ext(m1, m2)          # m1*u + m2*v = g
    if (a2 - a1) % g != 0:
        print(-1)
    else:
        m2g = m2 // g
        k = (a2 - a1) // g * u % m2g
        print(a1 + m1 * k)
```

(`u` is the inverse of `m1/g` modulo `m2/g`, straight from the first extended Euclid call.)

## Complexity

O(log min(m1, m2)) per query. A search over `k` is O(m2).

## Another way

Merge pairs into one congruence and repeat to combine many congruences: the result `(x, lcm)` of one merge is the input
`(a, m)` for the next. If all moduli are pairwise coprime, the classical formula `x = sum a_i * M_i * inverse(M_i, m_i)`
also works, but it fails when the moduli share factors.
