## Approach

Build `spf[i]` (smallest prime factor) for all `i <= 10^6` with a sieve. For a query, repeatedly take `p = spf[n]`, divide `n`
by `p` while possible to get the exponent `e`, and multiply `phi` by `p^(e-1) * (p - 1)` and `S` by
`p^(e-1) * (e * (p - 1) + p)`. Each query needs at most about 20 divisions.

Why the `S` formula: `S(p^e) = sum over i = 1..p^e of gcd(i, p^e)`. Group by the gcd: `p^k` for `k = 0..e`. The number of `i`
with `gcd = p^k` is `phi(p^(e-k))` (for `k = e` it is 1). That gives `sum_k p^k * phi(p^(e-k))`, which simplifies
to `p^(e-1) * (e*(p-1) + p)`.

## Code

```python
LIMIT = 10 ** 6
spf = list(range(LIMIT + 1))
for i in range(2, LIMIT + 1):
    if i * i > LIMIT:
        break
    if spf[i] == i:
        for m in range(i * i, LIMIT + 1, i):
            if spf[m] == m:
                spf[m] = i

q = int(input())
for _ in range(q):
    n = int(input())
    phi = 1
    total = 1
    while n > 1:
        p = spf[n]
        e = 0
        pe1 = 1
        while n % p == 0:
            n //= p
            e += 1
            if e > 1:
                pe1 *= p
        phi *= pe1 * (p - 1)
        total *= pe1 * (e * (p - 1) + p)
    print(phi, total)
```

## Complexity

O(L log log L) to build the table, O(log n) per query. A gcd loop is O(n log n) per query.

## Another way

Fill a `phi` table for every number in the sieve: start with `phi[i] = i`, and for each prime `p` and each multiple
`m` of `p` do `phi[m] -= phi[m] // p`. Then `phi` queries are table lookups. For `S`, use `S(n) = sum over d dividing n of d * phi(n / d)`.
