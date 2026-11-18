# Make change with the fewest coins (US coins)

A vending machine gives change in US coins: 25, 10, 5 and 1 cents. This coin system is **canonical** (chapter section 9): "largest coin first" always uses the fewest coins. Write `make_change(amount)` that returns the coins to give back.

Rules:

- `amount` is an integer, `0 <= amount <= 10**6`, in cents.
- Return a **list** of coins, **largest first**, that adds up to `amount` and uses as few coins as possible. `0` gives `[]`.
- The coin values are `25, 10, 5, 1`. You may keep them in a constant like `COINS = (25, 10, 5, 1)`.

## Example

```python
>>> make_change(30)
[25, 5]
>>> make_change(41)
[25, 10, 5, 1]
>>> make_change(4)
[1, 1, 1, 1]
>>> make_change(0)
[]
```

## Constraints

- One test asks for `make_change(1000019)`: that is 40,000 quarters and six more coins. Adding one coin per loop step is fine; looping one **cent** at a time would also work but is slow. Chapter section 9 shows `amount // c` and `amount % c`, which find how many of each coin in one step.

## Think about

Why is "largest first" safe for these coins, but not for `[1, 10, 25]` (try 30)? Chapter section 9, "Why does it work for 1, 2, 5, 10, ...?", has the idea.
