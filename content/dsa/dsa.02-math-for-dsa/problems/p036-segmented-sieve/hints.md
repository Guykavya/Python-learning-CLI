## Hint 1

How big must the base primes be? If a number `m <= r` is composite, its smallest prime factor `p` satisfies
`p * p <= m <= r`. So which primes are enough to cross off everything composite in `l..r`?

## Hint 2

For a base prime `p`, the first multiple of `p` that is `>= l` is `(l + p - 1) // p * p`. But `p` itself must **not** be crossed
off if it lies in the range, so start at `max(p * p, that multiple)`.

## Hint 3

```
base = primes up to sqrt(r) (ordinary sieve)
seg = [1] * (r - l + 1)
for p in base:
    start = max(p*p, ceil(l / p) * p)
    for m in range(start, r + 1, p): seg[m - l] = 0
for v in l..1: seg[v - l] = 0          # 0 and 1 are not prime
count and sum the positions still 1
```
