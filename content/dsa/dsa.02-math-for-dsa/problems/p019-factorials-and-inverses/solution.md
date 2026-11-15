## Approach

Division becomes multiplication by an inverse. `x^(p-2)` is the inverse of `x` modulo a prime `p` (Fermat). We build `fact` forward,
compute one inverse of the biggest factorial, then walk down to get all other inverse factorials in O(1) each.
After the O(N) precomputation, each query is three multiplications.

## Code

```python
import sys

MOD = 10**9 + 7
data = sys.stdin.read().split()
q = int(data[0])
pairs = [(int(data[1 + 2 * i]), int(data[2 + 2 * i])) for i in range(q)]
top = max(n for n, r in pairs)

fact = [1] * (top + 1)
for i in range(1, top + 1):
    fact[i] = fact[i - 1] * i % MOD

inv_fact = [1] * (top + 1)
inv_fact[top] = pow(fact[top], MOD - 2, MOD)
for i in range(top, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % MOD

out = []
for n, r in pairs:
    if r > n:
        out.append(0)
    else:
        out.append(fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD)
print("\n".join(map(str, out)))
```

## Complexity

O(N + q) after one `pow` (about 30 squarings). The table is about 10^6 entries, about 16 MB for two lists of ints.
Without the table, one query is O(r), so 10^5 queries are 10^11 steps.

## Another way

Compute an inverse per query: `pow(fact[r] * fact[n - r] % MOD, MOD - 2, MOD)`. It costs 30 steps per query,
fine for 10^5 queries, and simpler (no `inv_fact` table). Note that this works **only because `p` is prime**. For a composite modulus
use Pascal's triangle (if `n` is small) or the extended Euclid inverse when it exists.
