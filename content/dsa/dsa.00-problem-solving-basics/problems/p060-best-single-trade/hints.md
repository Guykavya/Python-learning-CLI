## Hint 1

Fix the sell day `S`. Among the days before `S`, which buy day gives the biggest profit? Now walk
through the days in order: can you keep that answer up to date as you go, without looking back?

## Hint 2

Keep `min_price` and `min_day`: the cheapest price seen **before** today, and the first day it
appeared. For each new day, first compute `price - min_price` (the best profit if you sell today),
and only then update the minimum with today's price. Update the best trade only when the profit is
**strictly greater** (so the earliest sell day survives ties), and update the minimum only when the
price is **strictly smaller** (so the earliest cheap day survives).

## Hint 3

```
min_price = first price; min_day = 1; best = 0
for day in 2..n:
    price = next price
    if price - min_price > best: best = price - min_price; buy = min_day; sell = day
    if price < min_price: min_price = price; min_day = day
print "profit", best
if best > 0: print "buy", buy, "sell", sell
```
Why must the profit check come before the minimum update? (Try a day whose price is a new minimum.)
