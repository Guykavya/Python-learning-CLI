## Approach

Chapter section 7: process the coins one at a time in the **outer** loop. After coin `c` is processed, `f[a]` = the number of combinations of `a` that use only the coins processed so far.

- When coin `c` is added, the combinations of `a` are those **without** `c` (the old `f[a]`) plus those with **at least one** `c`: remove one `c`, and what is left is a combination of `a - c` that may still use `c` (the **new** `f[a - c]`, already updated because `a` goes up).
- **Base:** `f[0] = 1`, the empty combination.

```python
def coin_ways(coins, amount):
    f = [0] * (amount + 1)
    f[0] = 1                         # one way to make 0: take nothing
    for c in coins:                  # outer loop: coins
        for a in range(c, amount + 1):
            f[a] += f[a - c]
    return f[amount]
```

Every combination is built in one fixed order (all of the first coin, then all of the second, ...), so it is counted exactly once.

| Outer loop | Inner loop | What `f[amount]` counts |
|---|---|---|
| coins | amounts | combinations (this problem) |
| amounts | coins | sequences (p020) |

## Complexity

`O(amount * len(coins))` time, `O(amount)` space.

## Another way

The 2-D table behind it: `g[i][a]` = combinations of `a` using only the first `i` coins. `g[i][a] = g[i - 1][a] + g[i][a - c]` (skip coin `i`, or take one more of it). The 1-D version above is this table with one row reused (chapter section 7, "The relation to dsa.07"). The test's brute force is its recursive form: choose how many copies of coin `i` to take, then go to coin `i + 1`.
