## Approach

Fix an order on the coins and make one decision at a time about the current coin: use it (the
amount shrinks, the coin stays available) or retire it (move to the next coin). Every
combination is produced exactly once. Many `(rest, i)` pairs repeat, so a dict memo turns an
exponential search into at most `amount × len(coins)` distinct subproblems. The memo lives in a
local of `count_ways`, captured by the inner closure, so each call starts with an empty memo.

## Code

```python
def count_ways(amount, coins):
    """Return the number of ways to make amount from unlimited coins of the given values."""
    memo = {}

    def ways(rest, i):
        if rest == 0:
            return 1
        if rest < 0 or i == len(coins):
            return 0
        key = (rest, i)
        if key not in memo:
            memo[key] = ways(rest - coins[i], i) + ways(rest, i + 1)
        return memo[key]

    return ways(amount, 0)
```

## Complexity

O(amount × number of coins) time and memo size; recursion depth up to about amount / smallest coin + number of coins (500 here, within the limit).

## Another way

The bottom-up loop (dynamic programming), with no recursion at all:
```python
ways = [1] + [0] * amount
for c in coins:
    for total in range(c, amount + 1):
        ways[total] += ways[total - c]
return ways[amount]
```
The DSA modules cover this technique in depth.
