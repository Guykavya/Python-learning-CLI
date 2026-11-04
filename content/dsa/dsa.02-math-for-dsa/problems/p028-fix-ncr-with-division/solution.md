## The three bugs

| # | bug | symptom | fix |
|---|---|---|---|
| 1 | `fact[n] // (fact[r] * fact[n - r])` divides **remainders** | wrong answers once `n >= 13` (when `n!` passes `10^9 + 7`) | multiply by the modular inverse of the denominator |
| 2 | `fact = [1] * MAXN` stops at index `MAXN - 1` | `IndexError` for `n = 10^6` | size `MAXN + 1`, loop to `MAXN` inclusive |
| 3 | `r > n` gives a negative index `n - r` | silent wrong answer (reads from the end of the list) | print 0 when `r > n` |

**Why bug 1 is wrong.** For small `n` the factorial is smaller than `MOD`, so `fact[n]` is the real factorial and the
division is exact, which is why the first tests pass. After that, `fact[n] = n! % MOD` and the remainder of a quotient is not the quotient of
remainders. The correct way: `a / b (mod p)` is `a * b^(p-2) (mod p)` for a prime `p`, because `b * b^(p-2) = b^(p-1) = 1`.

## Code

```python
MOD = 10 ** 9 + 7
MAXN = 10 ** 6

fact = [1] * (MAXN + 1)
for i in range(1, MAXN + 1):
    fact[i] = fact[i - 1] * i % MOD

q = int(input())
for _ in range(q):
    n, r = [int(x) for x in input().split()]
    if r < 0 or r > n:
        print(0)
    else:
        inv = pow(fact[r] * fact[n - r] % MOD, MOD - 2, MOD)
        print(fact[n] * inv % MOD)
```

## Complexity

O(MAXN) to build, then O(log MOD), about 30 multiplications, per query. For 100000 queries that is about 0.3 s.

## Another way

Precompute `inv_fact[i]` once (one `pow` for `inv_fact[MAXN]`, then walk downward with
`inv_fact[i - 1] = inv_fact[i] * i % MOD`). A query is then `fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD`
with no `pow` at all. That is the standard contest template (see the factorials problem).

## The general lesson

Modular arithmetic allows `+`, `-`, `*` freely. **Division is not allowed**: use the inverse. And always test the
boundary of a table: the smallest and the largest index.
