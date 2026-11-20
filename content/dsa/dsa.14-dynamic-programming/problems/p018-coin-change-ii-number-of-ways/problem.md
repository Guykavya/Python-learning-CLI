# Coin change II: number of ways

You have an unlimited supply of coins of each value in `coins`. Write `coin_ways(coins, amount)` that returns the number of **combinations** of coins that add up to exactly `amount` (chapter section 7).

Order does **not** matter: `1 + 1 + 2`, `1 + 2 + 1` and `2 + 1 + 1` are the same combination, counted once.

## Example

```python
>>> coin_ways([1, 2, 5], 5)       # 5, 2+2+1, 2+1+1+1, 1+1+1+1+1
4
>>> coin_ways([1, 2, 3], 4)       # 1+1+1+1, 1+1+2, 2+2, 1+3
4
>>> coin_ways([2], 3)
0
>>> coin_ways([7], 0)             # the empty combination
1
```

## Constraints

- `1 <= len(coins) <= 10`, different values from 1 to `10**4`, in any order.
- `0 <= amount <= 10**4`. Return the exact count.
- `O(amount * len(coins))`.

## Think about

Chapter section 7 has two loops that look almost the same. One counts combinations, the other counts sequences. Which loop must be **outside**, and why does that make each combination appear in only one order?
