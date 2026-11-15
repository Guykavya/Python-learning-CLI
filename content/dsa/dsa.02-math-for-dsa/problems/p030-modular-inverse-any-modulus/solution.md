## Approach

`a x = 1 (mod m)` has a solution exactly when `gcd(a, m) = 1`. Extended Euclid on `(a % m, m)` returns `g` and a pair with
`a*x + m*y = g`. When `g = 1`, reducing modulo `m` gives `a*x = 1 (mod m)`, so `x % m` is the inverse. When `g != 1`,
there is none. Reducing `a` first makes negative and huge `a` safe. For `m = 1`, `a % 1 = 0`, `ext(0, 1) = (1, 0, 1)`, and
`g = 1`, `0 % 1 = 0`: the answer 0 comes out without a special case.

## Code

```python
def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


q = int(input())
for _ in range(q):
    a, m = [int(x) for x in input().split()]
    a %= m
    g, x, y = ext(a, m)
    if g != 1:
        print(-1)
    else:
        print(x % m)
```

## Complexity

O(log m) per query, about 90 steps at most. The naive loop is O(m).

## Another way

Python 3.8 and later has `pow(a, -1, m)`, which raises `ValueError` when no inverse exists and handles any modulus.
For a **prime** `m`, Fermat gives `pow(a, m - 2, m)`. For the general case, Euler's theorem gives `a^(phi(m) - 1)`, but
you need `phi(m)`, which needs the factorisation of `m`: far slower than extended Euclid for `m` near 10^18.
