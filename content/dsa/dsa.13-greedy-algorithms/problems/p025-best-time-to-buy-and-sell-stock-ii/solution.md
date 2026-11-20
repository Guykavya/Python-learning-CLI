## Approach

Add every positive day-to-day rise. A trade from day `a` to day `b` earns `prices[b] - prices[a]`, which equals the sum of the daily changes between them. Keeping only the positive changes is at least as good as any set of trades, and it is achievable: buy before each rising day and sell at its end.

```python
def max_profit(prices):
    total = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            total += prices[i] - prices[i - 1]
    return total
```

The loop starts at 1, so an empty list or a single day gives 0.

## Complexity

`O(n)` time, `O(1)` space.

## Another way

Dynamic programming with two states per day (the safe tool when a greedy idea is in doubt, and the one that also solves variants with fees or cool-downs): `free` = best profit holding no share, `hold` = best profit holding one.

```python
def max_profit(prices):
    if not prices:
        return 0
    free, hold = 0, -prices[0]
    for p in prices[1:]:
        free, hold = max(free, hold + p), max(hold, free - p)
    return free
```
