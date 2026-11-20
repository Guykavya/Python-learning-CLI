# Best time to buy and sell stock II

`prices[i]` is the price of one share on day `i`. You may hold **at most one share** at a time, and you may buy and sell **as many times as you like** (you can sell and buy again on the same day). Write `max_profit(prices)` that returns the largest total profit (chapter section 11, "Best time to buy and sell stock (many trades)").

## Example

```python
>>> max_profit([7, 1, 5, 3, 6, 4])    # buy 1 sell 5, buy 3 sell 6
7
>>> max_profit([1, 2, 3, 4, 5])        # buy 1 sell 5 (= 1 + 1 + 1 + 1)
4
>>> max_profit([5, 4, 3, 2, 1])        # never buy
0
>>> max_profit([])
0
```

## Constraints

- `0 <= len(prices) <= 10**5`, `0 <= prices[i] <= 10**4`.

## Think about

This is **not** the one-trade problem (buy once, sell once). With one trade, `[7, 1, 5, 3, 6, 4]` gives 5. Why is the many-trade answer simply the sum of every day-to-day rise?
