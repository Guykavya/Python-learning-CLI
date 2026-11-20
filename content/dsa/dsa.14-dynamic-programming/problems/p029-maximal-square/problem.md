# Maximal square

`matrix` is a grid of `0`s and `1`s. Write `maximal_square(matrix)` that returns the **area** of the largest square made only of `1`s (chapter section 8). If there are no `1`s at all, the answer is 0.

## Example

```python
>>> maximal_square([[1, 0, 1, 0, 0],
...                 [1, 0, 1, 1, 1],
...                 [1, 1, 1, 1, 1],
...                 [1, 0, 0, 1, 0]])
4
>>> maximal_square([[1, 1, 1, 1]])     # a 1 by 4 rectangle holds only 1 by 1 squares
1
>>> maximal_square([[0, 0], [0, 0]])
0
>>> maximal_square([[1, 1], [1, 1]])
4
```

## Constraints

- `1 <= rows, cols <= 250`.
- Checking every square cell by cell is about `O(n^5)` and too slow on a 250 by 250 grid. Use the corner DP: `O(rows * cols)`.

## Think about

1. State: `f[r][c]` = the side of the largest all-ones square whose **bottom-right corner** is `(r, c)`. Why is "the largest square anywhere in the first `r` rows" a worse state?
2. A square of side `k` with its corner at `(r, c)` contains squares of side `k - 1` with corners at three neighbouring cells. Which three? Why does the **smallest** of their `f` values decide `f[r][c]`?
3. The function returns an **area**. Where is the largest side, and what do you do with it?
