## Hint 1

To avoid counting `1+2` and `2+1` twice, decide coin by coin. For the coin at index i: either use it at least once, or never use it again. What smaller problems do those two choices leave?

## Hint 2

`ways(rest, i)` = number of ways to make `rest` using only `coins[i:]`.
- `rest == 0`: 1 way. `rest < 0` or `i == len(coins)`: 0 ways.
- Otherwise `ways(rest - coins[i], i)` (use coin i again) `+ ways(rest, i + 1)` (skip it for good).

## Hint 3

```
def count_ways(amount, coins):
    memo = {}
    def ways(rest, i):
        if rest == 0: return 1
        if rest < 0 or i == len(coins): return 0
        key = (rest, i)
        if key not in memo:
            memo[key] = ways(rest - coins[i], i) + ways(rest, i + 1)
        return memo[key]
    return ways(amount, 0)
```
