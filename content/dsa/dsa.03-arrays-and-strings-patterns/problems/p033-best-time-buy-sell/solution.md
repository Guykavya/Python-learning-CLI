## Approach

For every possible selling day, the best buying day is the cheapest day before it. So walk through the prices
once, keeping the cheapest price seen so far. Each day, the profit of selling today is `price - cheapest`; keep
the largest. `best` starts at 0, which covers the "don't trade" choice.

This is the same shape as Kadane's algorithm: a running summary of the past (the minimum) and a running best.

## Code

```python
n = int(input())
prices = [int(x) for x in input().split()]

cheapest = prices[0]       # the lowest price on any day so far
best = 0                   # not trading at all earns 0
for p in prices[1:]:
    if p - cheapest > best:
        best = p - cheapest        # sell today, having bought on the cheapest earlier day
    if p < cheapest:
        cheapest = p
print(best)
```

| day | price | cheapest before | sell today | best |
|---|---|---|---|---|
| 1 | 7 | | | 0 |
| 2 | 1 | 7 | -6 | 0 |
| 3 | 5 | 1 | 4 | 4 |
| 4 | 3 | 1 | 2 | 4 |
| 5 | 6 | 1 | 5 | 5 |
| 6 | 4 | 1 | 3 | 5 |

## Complexity

O(n) time, O(1) extra memory. Trying every pair of days is O(n^2).

## Another way

Walk from the right and keep the **highest** price after each day: `best = max(best, highest_later - price)`.
Or turn it into Kadane: the profit of buying on day `i` and selling on day `j` is the sum of the daily changes
`prices[k+1] - prices[k]` between them, so the answer is the maximum subarray sum of the changes (or 0).
