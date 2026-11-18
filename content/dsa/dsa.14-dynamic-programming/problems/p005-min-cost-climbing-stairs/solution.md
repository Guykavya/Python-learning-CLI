## Approach

The recipe from chapter section 5:

- **State:** `f(i)` = the cheapest price to **arrive** at stair `i`, before paying `cost[i]`.
- **Transition:** you came from `i - 1` (paying `cost[i - 1]`) or from `i - 2` (paying `cost[i - 2]`): `f(i) = min(f(i-1) + cost[i-1], f(i-2) + cost[i-2])`.
- **Base:** `f(0) = f(1) = 0`, because you may start on either for free.
- **Answer:** `f(n)` with `n = len(cost)`, the top.

```python
def min_cost_climb(cost):
    n = len(cost)
    f = [0] * (n + 1)
    for i in range(2, n + 1):
        f[i] = min(f[i - 1] + cost[i - 1], f[i - 2] + cost[i - 2])
    return f[n]
```

## Complexity

`O(n)` time, `O(n)` space (or `O(1)` with two variables).

## Another way

Define the state the other way round: `g(i)` = the cheapest price from stair `i` to the top, **including** `cost[i]`. Then `g(i) = cost[i] + min(g(i + 1), g(i + 2))`, with `g(n) = g(n + 1) = 0`, filled from `i = n - 1` **down** to 0 (the arrows point right, so loop backwards, chapter section 4). The answer is `min(g(0), g(1))`. With rolling variables:

```python
def min_cost_climb(cost):
    a, b = 0, 0                     # g(i + 1), g(i + 2)
    for c in reversed(cost):
        a, b = c + min(a, b), a
    return min(a, b)
```
