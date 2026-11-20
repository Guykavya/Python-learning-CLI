## Approach

The recipe from chapter section 7:

- **State:** `f(a)` = the fewest coins that make exactly `a`.
- **Transition:** the last coin is some `c <= a`: `f(a) = 1 + min(f(a - c))`.
- **Base:** `f(0) = 0`. Unreachable amounts are infinity.
- **Answer:** `f(amount)`, or `-1` if it is still infinity.

```python
INF = float("inf")


def coin_change(coins, amount):
    f = [INF] * (amount + 1)
    f[0] = 0                                       # zero coins make 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and f[a - c] + 1 < f[a]:
                f[a] = f[a - c] + 1
    return f[amount] if f[amount] != INF else -1
```

Infinity is the right "impossible" value inside the table because `INF + 1 == INF` and `INF` never wins a `min`. A stored `-1` would win every `min` and would need a special case in every transition.

## Complexity

`O(amount * len(coins))` time, `O(amount)` space. For `amount = 10**4` and 12 coins that is 120,000 steps.

## Another way

**Breadth-first search on amounts.** Start at 0; each coin is an edge `x -> x + c`. The first time BFS reaches `amount`, the number of edges is the fewest coins (every edge costs 1). It is the same `O(amount * len(coins))` and can stop early. The plain recursion that tries every coin as the last one (the brute force in the tests) is the same DP without a notebook: exponential.
