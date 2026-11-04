## Hint 1

Do it first for a prime power, `p^e`. Which numbers in `1..p^e` share a factor with it? Only the multiples of `p`: there are
`p^(e-1)` of them. So `phi(p^e) = p^e - p^(e-1)`.

## Hint 2

For a general `n`, if `n = a * b` with `gcd(a, b) = 1`, then `phi(n) = phi(a) * phi(b)` and so does `S`. So compute the
exponent `e` of each prime `p` in `n`, get the factor for `p^e`, and multiply.

## Hint 3

```
spf = smallest prime factor of every number up to 10^6 (sieve once)
for each n:
    phi = 1; s = 1
    while n > 1:
        p = spf[n]; e = 0; pe1 = 1             # pe1 will be p^(e-1)
        while n % p == 0: n //= p; e += 1; (update pe1)
        phi *= pe1 * (p - 1); s *= pe1 * (e * (p - 1) + p)
```
