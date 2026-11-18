## Approach

A system is canonical exactly when greedy matches the fewest-coin count on every amount, and the Kozen-Zaks bound (chapter section 9) says the first mismatch, if there is one, comes before `c(k-1) + ck`. So compare greedy with the truth on amounts `1 .. c(k-1) + ck - 1`.

The truth comes from one table built from small to large: the best way to pay `a` ends with some coin `c`, after which `a - c` was paid in the best way, so `best[a] = 1 + min(best[a - c])`. This is the first **dynamic programming** table of the course; the later DP module builds many like it. It is just as correct as the BFS of section 9 and much cheaper when you need every amount.

```python
def greedy_count(amount, coins_desc):
    count = 0
    for c in coins_desc:
        count += amount // c
        amount %= c
    return count


def is_canonical(coins):
    coins = sorted(coins)
    if len(coins) < 2:
        return True                                   # only the 1 coin: one way to pay
    limit = coins[-1] + coins[-2] - 1                 # the first failure, if any, is <= limit
    desc = coins[::-1]
    best = [0] * (limit + 1)                          # best[a] = fewest coins for amount a
    for a in range(1, limit + 1):
        best[a] = 1 + min(best[a - c] for c in coins if c <= a)
        if greedy_count(a, desc) != best[a]:
            return False
    return True
```

## Complexity

`B = c(k-1) + ck`. The table costs `O(B * k)` and greedy costs `O(k)` per amount, so `O(B * k)` time and `O(B)` space. For coins up to 10,000 and `k <= 10` that is at most about 200,000 * 10 steps.

## Another way

The chapter's version: `first_failure(coins, bound - 1) is None`, with a BFS per amount. Correct, but each BFS costs `O(amount * k)`, so the whole check is `O(B^2 * k)`, too slow for coins near 10,000. There is also a polynomial test by Pearson (1994), `O(k^3)`, independent of the coin sizes: it builds a small set of candidate amounts from the greedy representations of `c(i) - 1` and checks only those. Worth reading about after the DP module.
