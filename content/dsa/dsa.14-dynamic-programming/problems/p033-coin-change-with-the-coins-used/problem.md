# Coin change with the coins used

You have coins of the values in `coins` (as many of each as you like). Write `coins_used(coins, amount)` that returns a **list of coins** adding up to exactly `amount` and using the **fewest coins possible**, or `None` if the amount cannot be made (chapter sections 7 and 9).

## Example

```python
>>> coins_used([1, 2, 5], 11)        # 3 coins; any order is fine
[1, 5, 5]
>>> coins_used([1, 3, 4], 6)         # greedy would give [4, 1, 1]
[3, 3]
>>> coins_used([2], 3)
>>> coins_used([7], 0)               # nothing to pay: no coins
[]
```

The tests **validate** your list: every coin must come from `coins`, they must add up to `amount`, and there must be as few of them as possible. Any such list is accepted, in any order.

## Constraints

- `1 <= len(coins) <= 10`, `1 <= coins[i] <= 1000`, all different; `0 <= amount <= 10**4`.
- Write it bottom-up. A memoised recursion would go up to 10,000 calls deep with a coin of value 1.

## Think about

1. Section 9 offers two methods: store `last[a]` (the coin that gave the best `f[a]`), or re-derive the coin from the table afterwards. Which one will you use?
2. If `f[a]` was reached with the coin `c` as the last coin, which amount do you step back to?
3. Where must the line `last[a] = c` go so that it remembers the **best** coin, not just the last coin tried?
