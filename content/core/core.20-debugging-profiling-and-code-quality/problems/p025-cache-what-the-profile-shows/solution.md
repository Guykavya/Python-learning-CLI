## Approach

The profile says `count` was called 74,809 times (`74809/1`: 74,809 in total, 1 from outside).
But `count(amount, coins, i)` only depends on its arguments, and there are just 61 × 7 different
`(amount, i)` pairs for one coin list. So the same answers are computed again and again. That
is the classic case for **memoisation**: remember each answer the first time, look it up after.

`functools.cache` stores results in a dictionary keyed by the arguments. Arguments must be
hashable, which is why `ways` turns the list into a tuple **before** calling the cached
function. Because `coins` is one of the arguments, two coin lists never mix answers.

## Code

```python
from functools import cache


def ways(amount, coins):
    return count(amount, tuple(coins), 0)


@cache
def count(amount, coins, i):
    if amount == 0:
        return 1
    if amount < 0 or i == len(coins):
        return 0
    return count(amount - coins[i], coins, i) + count(amount, coins, i + 1)
```

Profile after (same input, real run): the line for `count` becomes
`508/1    0.000    0.000    0.001    0.001 solution.py:9(count)`, 508 calls instead of 74,809, and
the whole call takes about a millisecond (machine-specific).

## Complexity

O(amount × len(coins)) different calls, each O(1) apart from the recursion. Memory: one cache
entry per call, and the recursion goes up to about `amount` deep (with a coin of 1). For very
large amounts that depth would hit Python's recursion limit; then use the loop version below.

## Another way

Bottom-up dynamic programming, no recursion and no cache:

```python
def ways(amount, coins):
    table = [1] + [0] * amount          # table[a] = ways to pay a with the coins seen so far
    for coin in coins:
        for a in range(coin, amount + 1):
            table[a] += table[a - coin]
    return table[amount]
```

That is the same idea (each sub-answer computed once), written as a loop.
