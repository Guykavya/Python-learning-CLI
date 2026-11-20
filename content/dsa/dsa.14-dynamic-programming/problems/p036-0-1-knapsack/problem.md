# 0/1 knapsack

Item `i` weighs `wt[i]` and is worth `val[i]`. A bag holds total weight at most `W`. Each item may be taken **at most once**. Write two functions (chapter section 10):

1. `knapsack_table(wt, val, W)` returns the full 2-D table `f`, a list of `len(wt) + 1` rows of `W + 1` numbers, where `f[i][w]` is the best value using only the first `i` items with capacity `w`.
2. `knapsack(wt, val, W)` returns only the best value, using **one** list of `W + 1` numbers (the one-dimensional version).

Write the table first: it is the definition. Then squeeze it into one row.

## Example

```python
>>> for row in knapsack_table([1, 3, 4, 5], [1, 4, 5, 7], 7):
...     print(row)
[0, 0, 0, 0, 0, 0, 0, 0]
[0, 1, 1, 1, 1, 1, 1, 1]
[0, 1, 1, 4, 5, 5, 5, 5]
[0, 1, 1, 4, 5, 6, 6, 9]
[0, 1, 1, 4, 5, 7, 8, 9]
>>> knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7)
9
>>> knapsack([2], [10], 7)        # one item: it can be taken once
10
>>> knapsack([8, 9], [5, 6], 7)   # nothing fits
0
```

## Constraints

- `0 <= len(wt) == len(val) <= 200`; weights from 1 to 1000, values from 0 to 10**6.
- `0 <= W <= 10**4`.
- `O(len(wt) * W)` time; `knapsack` uses `O(W)` memory.

## Think about

1. In the table, "take item `i - 1`" reads `f[i - 1][w - wt[i - 1]]`: the row **above**. What does that row promise about item `i - 1`?
2. In one list, the cell `g[w - wt]` must still hold the "row above" value when `g[w]` reads it. Which direction must the `w` loop go for that?
3. Why does `knapsack([2], [10], 7)` give 30 if the loop goes the other way?
