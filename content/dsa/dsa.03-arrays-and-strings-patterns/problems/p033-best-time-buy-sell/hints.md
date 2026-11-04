## Hint 1

Fix the selling day `j`. Which buying day gives the most profit for that sale? You only need one number about the
days before `j`.

## Hint 2

The best buy for a sale on day `j` is the **cheapest** price on days `0..j-1`. Keep that minimum as you walk. For each
day: first try selling today against the cheapest earlier price, then update the cheapest price with today's.

## Hint 3

```
cheapest = prices[0]; best = 0
for p in prices[1:]:
    best = max(best, p - cheapest)
    cheapest = min(cheapest, p)
print best
```
