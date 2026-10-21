## Approach

Fix a sell day `S`. The best buy day for it is simply the cheapest day before `S`. So while walking
through the days in order, remember only the cheapest price so far (`min_price`) and the first day it
appeared (`min_day`). For each new day:

1. **Profit if I sell today:** `price - min_price`, where the minimum covers only earlier days. If it
   is strictly greater than the best so far, record this trade.
2. **Then** update the minimum with today's price, if it is strictly smaller.

The order matters: computing the profit first guarantees the buy day is before the sell day.

**Ties.** Days are visited in increasing order, so the first sell day that reaches the best profit is
the earliest; updating only on a strictly greater profit keeps it. Likewise, updating the minimum only
on a strictly smaller price keeps the earliest of several equally cheap days.

## Trace

Prices `3 8 1 5`:

| day | price | profit (price - min) | best | buy | sell | min_price | min_day |
|---|---|---|---|---|---|---|---|
| 1 | 3 | | 0 | | | 3 | 1 |
| 2 | 8 | 5 | 5 | 1 | 2 | 3 | 1 |
| 3 | 1 | -2 | 5 | 1 | 2 | 1 | 3 |
| 4 | 5 | 4 | 5 | 1 | 2 | 1 | 3 |

Output: `profit 5`, `buy 1 sell 2`.

## Code

```python
n = int(input())

min_price = int(input())     # cheapest price seen so far
min_day = 1                  # the first day it was that cheap
best = 0
buy_day = 0
sell_day = 0

for day in range(2, n + 1):
    price = int(input())
    # Selling today, the best buy is the cheapest earlier day.
    profit = price - min_price
    if profit > best:            # strictly greater: keep the earliest sell day on ties
        best = profit
        buy_day = min_day
        sell_day = day
    if price < min_price:        # strictly smaller: keep the earliest cheapest day
        min_price = price
        min_day = day

print(f"profit {best}")
if best > 0:
    print(f"buy {buy_day} sell {sell_day}")
```

## Complexity

One pass with constant work per day: O(n) time and O(1) memory. The all-pairs method is O(n^2), about
5 * 10^9 pairs for `n = 100000`, which would take hours in Python.

## Another way

**Track the best price to sell at, walking backwards.** Going from the last day to the first, keep the
highest price seen so far and compute `max_later - price` for each buy day. It is the mirror image of
the method above, but it needs all prices stored (you cannot read input backwards), and the tie rules
are harder to get right. A different idea: the profit is the sum of day-to-day changes between the buy
and sell day, so the problem becomes "the largest sum of consecutive changes" (Kadane's algorithm),
which you will meet later in the course.

## Edge cases

- `n = 1`: the loop never runs; `profit 0`.
- Falling or flat prices: no strictly positive profit; only `profit 0` is printed.
- The lowest price after the best trade (`3 8 1 5`): the running minimum handles it naturally.
