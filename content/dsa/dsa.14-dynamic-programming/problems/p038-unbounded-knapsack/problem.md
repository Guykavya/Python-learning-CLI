# Unbounded knapsack

Same as the 0/1 knapsack (p036), but now there is an **unlimited** supply of every item: item `i` weighs `wt[i]`, is worth `val[i]`, and may be taken any number of times. Write `unbounded_knapsack(wt, val, W)` that returns the largest total value with total weight at most `W` (chapter section 11).

## Example

```python
>>> unbounded_knapsack([2, 3], [10, 14], 7)    # 2 + 2 + 3
34
>>> unbounded_knapsack([4, 5], [7, 9], 12)     # 4 + 4 + 4
21
>>> unbounded_knapsack([5], [1], 4)            # nothing fits
0
>>> unbounded_knapsack([2], [10], 7)           # three copies, weight 6
30
```

## Constraints

- `0 <= len(wt) == len(val) <= 50`; weights from 1 to 1000, values from 0 to 10**6.
- `0 <= W <= 10**5`.
- `O(len(wt) * W)` time, `O(W)` memory.

## Think about

1. In p036 the one-list loop went **downwards** so that `g[w - wt]` was still the old value. Here you **want** `g[w - wt]` to possibly include the same item already. Which direction gives that?
2. Is the answer for capacity `w` ever smaller than the answer for capacity `w - 1`? What does that say about the leftover space?
3. Can the unbounded answer ever be smaller than the 0/1 answer for the same input?
