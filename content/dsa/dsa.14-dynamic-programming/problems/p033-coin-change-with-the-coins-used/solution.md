## Approach

Parent pointers (section 9, method 1). Next to `f[a]` keep `last[a]`, the final coin of a best way to make `a`. Then a best way to make `a` is "a best way to make `a - last[a]`, plus that coin": walking `a -> a - last[a] -> ... -> 0` lists the coins.

```python
INF = float("inf")


def coins_used(coins, amount):
    f = [INF] * (amount + 1)
    last = [None] * (amount + 1)         # last[a] = the coin used last in a best way to make a
    f[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and f[a - c] + 1 < f[a]:
                f[a] = f[a - c] + 1
                last[a] = c              # only when this coin is the new best
    if f[amount] == INF:
        return None
    used = []
    a = amount
    while a > 0:
        used.append(last[a])
        a -= last[a]                     # step back to the smaller amount
    return used
```

The walk back takes exactly `f[amount]` steps, so the list has the minimum length. Each step lands on an amount whose `f` is one less, which is never `INF` (it was used to make `f[a]`), so `last` there is always set.

When several coins tie, the first one tried wins (`<`, not `<=`). Another order gives another list with the same length; that is why the tests validate instead of comparing lists.

## Complexity

`O(amount * len(coins))` time, `O(amount)` space; the walk back is `O(f[amount])`.

## Another way

Re-derive the coin from the table (section 9, method 2): keep only `f`; walking back, at amount `a` look for any coin `c` with `f[a - c] + 1 == f[a]`, take it, and continue from `a - c`. No second list, a little more work on the way back.
