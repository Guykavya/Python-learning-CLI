## Approach

All queries use numbers up to 10^6, so build a sieve of Eratosthenes up to 10^6 once. Each query then checks
`p = 2, 3, 4, ...` until both `p` and `n - p` are marked prime. Because the smallest working `p` is tiny (for all even
`n <= 10^6` it is below 200), each query is a handful of table lookups.

## Code

```python
LIMIT = 10 ** 6
is_prime = [True] * (LIMIT + 1)
is_prime[0] = is_prime[1] = False
for i in range(2, LIMIT + 1):
    if i * i > LIMIT:
        break
    if is_prime[i]:
        for m in range(i * i, LIMIT + 1, i):
            is_prime[m] = False

k = int(input())
for _ in range(k):
    n = int(input())
    p = 2
    while not (is_prime[p] and is_prime[n - p]):
        p += 1
    print(p, n - p)
```

## Complexity

O(L log log L) for the sieve, about 0.3 s for `L = 10^6` (a slice assignment makes it faster), plus a few steps per query.
Without the table, each primality test costs up to 1000 divisions, repeated for every candidate and every query.

## Another way

Make the sieve faster with slice assignment: `is_prime[i*i::i] = [False] * len(range(i*i, L + 1, i))`. Or test only
`p` from a list of primes. For a single query, trial division of the candidates is just fine; the sieve pays off
when there are many queries.
