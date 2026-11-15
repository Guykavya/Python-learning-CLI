## Approach

Reduce `a` and `b` modulo `m`. Let `g = gcd(a, m)`. If `g` does not divide `b`, the answer is `-1`: `a*x - k*m = b` and `g`
divides the left side. Otherwise divide `a`, `b`, `m` by `g`: now `gcd(a', m') = 1`, so `a'` has an inverse `inv` modulo
`m'`, and `x = b' * inv % m'` is the unique solution in `0..m'-1`. It is also the smallest of the `g` solutions
`x, x + m', x + 2m', ...` modulo `m`.

## Code

```python
def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


q = int(input())
for _ in range(q):
    a, b, m = [int(x) for x in input().split()]
    a %= m
    b %= m
    g, _x, _y = ext(a, m)
    if b % g != 0:
        print(-1)
    else:
        a2, b2, m2 = a // g, b // g, m // g
        g2, inv, _y2 = ext(a2 % m2, m2)
        print(b2 * inv % m2)
```

For `m2 = 1`: `a2 % 1 = 0`, `ext(0, 1) = (1, 0, 1)`, so `inv = 0` and the answer is `0`. When `a = 0` (and `m > 1`), `g = m`: `b % m` is
zero or not; if it is zero, `m2 = 1` and the answer is 0.

## Complexity

O(log m) per query. A loop over `x` is O(m).

## Another way

Run the extended Euclid on `(a, m)` once: it gives `a*x0 + m*y0 = g`. Then `x = x0 * (b // g) % (m // g)`. This skips the second `ext`
call, because the first already gave the coefficient (it is the inverse of `a/g` modulo `m/g`).
