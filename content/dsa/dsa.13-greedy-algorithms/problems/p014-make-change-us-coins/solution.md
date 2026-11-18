## Approach

Largest coin first (chapter section 9). For each coin, from 25 down to 1, take it as many times as it fits; the rest of the amount is passed to the next coin. With `//` this is one step per coin, not one step per coin given.

```python
COINS = (25, 10, 5, 1)


def make_change(amount):
    used = []
    for c in COINS:                      # already largest first
        count = amount // c              # how many of this coin fit
        used.extend([c] * count)
        amount -= count * c
    return used
```

Why it is safe for US coins (the exchange sketch of section 9): a fewest-coin answer never has five 1s (one 5 is better), never two 5s (one 10), never three 10s (25 + 5 is better), and never two 10s together with a 5 (25 is better). So the coins below 25 add up to at most 24, which means the number of quarters must be the greedy number, `amount // 25`. The same reasoning fixes the 10s, then the 5s.

The test checks every amount from 0 to 200 against a table that tries every last coin, so a shortcut that is right "most of the time" is caught.

## Complexity

`O(k)` steps for `k` coin types, plus the time to build the output list, which has one entry per coin given (`O(amount / 25)` in the worst case).

## Another way

A `while amount >= c` loop per coin (chapter section 1): the same answer, one coin per step. Or return counts instead of a list, like `{25: 1, 5: 1}` for 30, which is `O(k)` with no long list; real cash machines think in counts.
