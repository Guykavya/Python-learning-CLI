## Approach

Build the `spf` (smallest prime factor) table up to the largest query. Then each query is factorised in
`O(number of prime factors)` steps by reading `spf`. Multiply `(e + 1)` over the exponents.

## Code

```python
import sys

data = sys.stdin.read().split()
q = int(data[0])
queries = [int(x) for x in data[1:1 + q]]
top = max(queries)

spf = list(range(top + 1))
i = 2
while i * i <= top:
    if spf[i] == i:
        for m in range(i * i, top + 1, i):
            if spf[m] == m:
                spf[m] = i
    i += 1

out = []
for n in queries:
    ans = 1
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        ans *= e + 1
    out.append(ans)
print("\n".join(map(str, out)))
```

## Complexity

Sieve `O(N log log N)`, each query `O(log n)`. About 3 million sieve steps plus at most 20 steps per query.
Trial division per query is `O(sqrt n)` = 1000 steps, which is 10^8 for 10^5 queries.

## Another way

Compute the divisor count of **every** number by a harmonic sum: `for d in range(1, N + 1): for m in range(d, N + 1, d): cnt[m] += 1`.
That is about `N ln N` = 14 million steps, slower in Python but very simple, and it answers all queries by lookup.
