## Hint 1

Draw the prices as a line chart. A trade "buy at the bottom of a rise, sell at the top" earns the height of the rise. A long rise from 1 to 5 in steps of 1: is buying at 1 and selling at 5 different from four one-day trades?

## Hint 2

Every day where the price goes **up** from yesterday, you can earn that rise. Days where it goes down, you stay out. No other plan can earn more, because any trade's profit is the sum of the day-to-day changes it spans, and the falls inside it only reduce it.

## Hint 3

```
total = 0
for i in range(1, len(prices)):
    if prices[i] > prices[i - 1]:
        total += prices[i] - prices[i - 1]
return total
```
