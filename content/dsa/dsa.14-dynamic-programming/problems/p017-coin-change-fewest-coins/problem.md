# Coin change: fewest coins

You have an unlimited supply of coins of each value in `coins`. Write `coin_change(coins, amount)` that returns the **fewest coins** that add up to exactly `amount`, or `-1` if no combination does (chapter section 7).

## Example

```python
>>> coin_change([1, 2, 5], 11)        # 5 + 5 + 1
3
>>> coin_change([1, 3, 4], 6)         # 3 + 3; greedy (4 + 1 + 1) uses 3 coins
2
>>> coin_change([2], 3)
-1
>>> coin_change([7], 0)               # no coins needed
0
```

## Constraints

- `1 <= len(coins) <= 12`, coin values are different integers from 1 to `10**4`, in any order.
- `0 <= amount <= 10**4`.
- `O(amount * len(coins))`. Fill a table: a recursion down from `amount` with a 1-coin is 10,000 calls deep.
- Return an `int`: `-1`, not `float("inf")`, when the amount cannot be made.

## Think about

Why does the chapter use infinity for "cannot be made" inside the table, and only turn it into `-1` at the very end? What would go wrong if `-1` were stored in the table and used in `min`?
